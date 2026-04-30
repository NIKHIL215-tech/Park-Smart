package com.parksmart.handler;

import com.parksmart.dao.*;
import com.parksmart.model.*;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.*;
import java.util.regex.*;

/**
 * Single HTTP handler that routes all /api/* requests.
 *
 * Routes
 * ------
 * GET  /api/stats
 * GET  /api/slots[?floor=N]
 * POST /api/slots                  { floor, type }
 * GET  /api/bookings[?user_id=N]
 * POST /api/bookings               { vehicle, vehicle_type, slot_id, user_id, name }
 * POST /api/bookings/exit          { booking_id }
 * GET  /api/users
 * POST /api/users/login            { email, password }
 * POST /api/users/register         { name, email, phone, password }
 */
public class ApiHandler implements HttpHandler {

    private final UserDAO    userDAO    = new UserDAO();
    private final SlotDAO    slotDAO    = new SlotDAO();
    private final BookingDAO bookingDAO = new BookingDAO();
    private final PaymentDAO paymentDAO = new PaymentDAO();

    @Override
    public void handle(HttpExchange ex) throws IOException {
        // CORS headers for every response
        ex.getResponseHeaders().add("Access-Control-Allow-Origin",  "*");
        ex.getResponseHeaders().add("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        ex.getResponseHeaders().add("Access-Control-Allow-Headers", "Content-Type");
        ex.getResponseHeaders().add("Content-Type", "application/json; charset=utf-8");

        String method = ex.getRequestMethod().toUpperCase();
        String path   = ex.getRequestURI().getPath();

        // Preflight
        if ("OPTIONS".equals(method)) { send(ex, 200, "{}"); return; }

        try {
            if (path.equals("/api/stats") && "GET".equals(method)) {
                handleGetStats(ex);
            } else if (path.equals("/api/slots") && "GET".equals(method)) {
                handleGetSlots(ex);
            } else if (path.equals("/api/slots") && "POST".equals(method)) {
                handleAddSlot(ex);
            } else if (path.equals("/api/bookings") && "GET".equals(method)) {
                handleGetBookings(ex);
            } else if (path.equals("/api/bookings") && "POST".equals(method)) {
                handleCreateBooking(ex);
            } else if (path.equals("/api/bookings/exit") && "POST".equals(method)) {
                handleProcessExit(ex);
            } else if (path.equals("/api/users") && "GET".equals(method)) {
                handleGetUsers(ex);
            } else if (path.equals("/api/users/login") && "POST".equals(method)) {
                handleLogin(ex);
            } else if (path.equals("/api/users/register") && "POST".equals(method)) {
                handleRegister(ex);
            } else {
                send(ex, 404, err("Endpoint not found: " + method + " " + path));
            }
        } catch (SQLException e) {
            System.err.println("[DB ERROR] " + e.getMessage());
            send(ex, 500, err("Database error: " + e.getMessage()));
        }
    }

    // ─── Route Handlers ─────────────────────────────────────────────────────

    private void handleGetStats(HttpExchange ex) throws IOException, SQLException {
        int    avail    = slotDAO.countAvailable();
        int    occupied = slotDAO.countOccupied();
        int    active   = bookingDAO.countActive();
        double revenue  = paymentDAO.getTotalRevenue();

        send(ex, 200, String.format(
            "{\"avail\":%d,\"occupied\":%d,\"active\":%d,\"revenue\":%.2f}",
            avail, occupied, active, revenue));
    }

    private void handleGetSlots(HttpExchange ex) throws IOException, SQLException {
        Map<String, String> qp    = queryParams(ex);
        Integer             floor = qp.containsKey("floor") ? Integer.parseInt(qp.get("floor")) : null;
        List<Slot>          slots = slotDAO.getAllSlots(floor);
        send(ex, 200, toArray(slots));
    }

    private void handleAddSlot(HttpExchange ex) throws IOException, SQLException {
        String body  = readBody(ex);
        int    floor = extractInt(body, "floor");
        String type  = extractString(body, "type");
        if (floor < 1 || type == null) { send(ex, 400, err("floor and type required")); return; }
        slotDAO.addSlot(floor, type);
        send(ex, 200, ok("Slot added"));
    }

    private void handleGetBookings(HttpExchange ex) throws IOException, SQLException {
        Map<String, String> qp     = queryParams(ex);
        Integer             userId = qp.containsKey("user_id") ? Integer.parseInt(qp.get("user_id")) : null;
        List<Booking>       list   = bookingDAO.getAllBookings(userId);
        send(ex, 200, toArray(list));
    }

    private void handleCreateBooking(HttpExchange ex) throws IOException, SQLException {
        String body        = readBody(ex);
        String vehicle     = extractString(body, "vehicle");
        String vehicleType = extractString(body, "vehicle_type");
        int    slotId      = extractInt(body, "slot_id");
        int    userId      = extractInt(body, "user_id");
        String name        = extractString(body, "name");
        String entryStr    = extractString(body, "entry_time"); // "YYYY-MM-DDTHH:MM"

        if (vehicle == null || vehicleType == null || slotId < 1) {
            send(ex, 400, err("vehicle, vehicle_type and slot_id are required")); return;
        }

        // Parse and validate entry time
        Timestamp entryTime = null;
        if (entryStr != null && !entryStr.isBlank()) {
            try {
                String normalized = entryStr.replace("T", " ");
                if (normalized.length() == 16) normalized += ":00";
                entryTime = Timestamp.valueOf(normalized);
            } catch (IllegalArgumentException e) {
                send(ex, 400, err("Invalid entry_time format. Use YYYY-MM-DDTHH:MM")); return;
            }
            long minAllowed = System.currentTimeMillis() + 55 * 60 * 1000; // 55-min buffer (allows for clock skew)
            if (entryTime.getTime() < minAllowed) {
                send(ex, 400, err("Entry time must be at least 1 hour from now")); return;
            }
        }

        Slot slot = slotDAO.getById(slotId);
        if (slot == null || !"Available".equals(slot.status)) {
            send(ex, 409, err("Slot is not available")); return;
        }

        // Guest user: create a temporary account
        if (userId == 0 && name != null && !name.isBlank()) {
            User guest = new User();
            guest.name     = name;
            guest.email    = name.toLowerCase().replaceAll("\\s+", "") + "_" + System.currentTimeMillis() + "@guest.com";
            guest.phone    = "N/A";
            guest.password = "guest";
            userId = userDAO.register(guest);
        }

        // Create booking with the selected entry time
        int bookingId = bookingDAO.createBooking(userId, vehicle, vehicleType, slotId, entryTime);
        if (bookingId < 0) { send(ex, 500, err("Failed to create booking")); return; }

        // Create pending payment
        paymentDAO.createPending(bookingId);

        // Mark slot as Occupied
        slotDAO.updateStatus(slotId, "Occupied");

        send(ex, 200, String.format(
            "{\"success\":true,\"booking_id\":%d,\"message\":\"Booking confirmed for slot S%d\"}", bookingId, slotId));
    }

    private void handleProcessExit(HttpExchange ex) throws IOException, SQLException {
        String body      = readBody(ex);
        int    bookingId = extractInt(body, "booking_id");
        if (bookingId < 1) { send(ex, 400, err("booking_id required")); return; }

        double fee = bookingDAO.processExit(bookingId); // transactional
        send(ex, 200, String.format(
            "{\"success\":true,\"fee\":%.2f,\"message\":\"Exit processed. Fee: ₹%.0f\"}", fee, fee));
    }

    private void handleGetUsers(HttpExchange ex) throws IOException, SQLException {
        send(ex, 200, toArray(userDAO.getAllUsers()));
    }

    private void handleLogin(HttpExchange ex) throws IOException, SQLException {
        String body     = readBody(ex);
        String email    = extractString(body, "email");
        String password = extractString(body, "password");
        if (email == null || password == null) { send(ex, 400, err("email and password required")); return; }

        User user = userDAO.login(email, password);
        if (user == null) { send(ex, 401, err("Invalid email or password")); return; }

        send(ex, 200, String.format(
            "{\"success\":true,\"user\":%s}", user.toJson()));
    }

    private void handleRegister(HttpExchange ex) throws IOException, SQLException {
        String body     = readBody(ex);
        String name     = extractString(body, "name");
        String email    = extractString(body, "email");
        String phone    = extractString(body, "phone");
        String password = extractString(body, "password");

        if (name == null || email == null || phone == null || password == null) {
            send(ex, 400, err("All fields are required")); return;
        }
        if (userDAO.emailExists(email)) {
            send(ex, 409, err("Email already registered")); return;
        }

        User u = new User();
        u.name = name; u.email = email; u.phone = phone; u.password = password;
        int id = userDAO.register(u);

        send(ex, 200, String.format("{\"success\":true,\"id\":%d,\"message\":\"Account created\"}", id));
    }

    // ─── Helpers ─────────────────────────────────────────────────────────────

    private void send(HttpExchange ex, int code, String json) throws IOException {
        byte[] bytes = json.getBytes(StandardCharsets.UTF_8);
        ex.sendResponseHeaders(code, bytes.length);
        try (OutputStream os = ex.getResponseBody()) { os.write(bytes); }
    }

    private String readBody(HttpExchange ex) throws IOException {
        try (InputStream is = ex.getRequestBody()) {
            return new String(is.readAllBytes(), StandardCharsets.UTF_8);
        }
    }

    private Map<String, String> queryParams(HttpExchange ex) {
        Map<String, String> map   = new HashMap<>();
        String              query = ex.getRequestURI().getQuery();
        if (query == null || query.isEmpty()) return map;
        for (String pair : query.split("&")) {
            String[] kv = pair.split("=", 2);
            if (kv.length == 2) map.put(kv[0], kv[1]);
        }
        return map;
    }

    private String extractString(String json, String key) {
        Matcher m = Pattern.compile("\"" + key + "\"\\s*:\\s*\"([^\"]*)\"|\"" + key + "\"\\s*:\\s*'([^']*)'").matcher(json);
        if (m.find()) return m.group(1) != null ? m.group(1) : m.group(2);
        return null;
    }

    private int extractInt(String json, String key) {
        Matcher m = Pattern.compile("\"" + key + "\"\\s*:\\s*(-?\\d+)").matcher(json);
        return m.find() ? Integer.parseInt(m.group(1)) : 0;
    }

    private String ok(String msg) {
        return "{\"success\":true,\"message\":\"" + msg + "\"}";
    }

    private String err(String msg) {
        return "{\"success\":false,\"message\":\"" + msg.replace("\"", "'") + "\"}";
    }

    private <T extends Object> String toArray(List<T> list) {
        StringBuilder sb = new StringBuilder("[");
        for (int i = 0; i < list.size(); i++) {
            if (i > 0) sb.append(",");
            Object item = list.get(i);
            if      (item instanceof User)    sb.append(((User)    item).toJson());
            else if (item instanceof Slot)    sb.append(((Slot)    item).toJson());
            else if (item instanceof Booking) sb.append(((Booking) item).toJson());
        }
        return sb.append("]").toString();
    }
}
