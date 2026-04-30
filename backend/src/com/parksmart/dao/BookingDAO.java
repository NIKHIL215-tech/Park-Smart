package com.parksmart.dao;

import com.parksmart.DBConnection;
import com.parksmart.model.Booking;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class BookingDAO {

    private static final String SELECT_SQL =
        "SELECT b.id, b.user_id, COALESCE(u.name,'Guest') AS user_name, " +
        "       b.vehicle, b.vehicle_type, b.slot_id, " +
        "       COALESCE(ps.floor, 0) AS slot_floor, " +
        "       DATE_FORMAT(b.entry_time,'%Y-%m-%dT%H:%i:%s') AS entry_time, " +
        "       DATE_FORMAT(b.exit_time, '%Y-%m-%dT%H:%i:%s') AS exit_time, " +
        "       b.total_fee, b.status, " +
        "       COALESCE(p.status,'Pending') AS payment_status " +
        "FROM bookings b " +
        "LEFT JOIN users          u  ON b.user_id    = u.id  " +
        "LEFT JOIN parking_slots  ps ON b.slot_id    = ps.id " +
        "LEFT JOIN payments       p  ON p.booking_id = b.id  ";

    public List<Booking> getAllBookings(Integer userId) throws SQLException {
        List<Booking> list = new ArrayList<>();
        String sql = SELECT_SQL + (userId != null ? "WHERE b.user_id = ? " : "") + "ORDER BY b.entry_time DESC";

        try (Connection conn = DBConnection.getConnection()) {
            ResultSet rs;
            if (userId != null) {
                PreparedStatement ps = conn.prepareStatement(sql);
                ps.setInt(1, userId);
                rs = ps.executeQuery();
            } else {
                rs = conn.createStatement().executeQuery(sql);
            }
            while (rs.next()) list.add(map(rs));
            rs.close();
        }
        return list;
    }

    public Booking getById(int id) throws SQLException {
        String sql = SELECT_SQL + "WHERE b.id = ?";

        try (Connection      conn = DBConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setInt(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? map(rs) : null;
            }
        }
    }

    public int createBooking(int userId, String vehicle, String vehicleType, int slotId, Timestamp entryTime) throws SQLException {
        String sql = "INSERT INTO bookings (user_id, vehicle, vehicle_type, slot_id, entry_time, status) " +
                     "VALUES (?, ?, ?, ?, ?, 'Active')";

        try (Connection      conn = DBConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {

            ps.setInt(1, userId);
            ps.setString(2, vehicle);
            ps.setString(3, vehicleType);
            ps.setInt(4, slotId);
            ps.setTimestamp(5, entryTime != null ? entryTime : new Timestamp(System.currentTimeMillis()));
            ps.executeUpdate();

            try (ResultSet keys = ps.getGeneratedKeys()) {
                return keys.next() ? keys.getInt(1) : -1;
            }
        }
    }

    /**
     * Processes vehicle exit atomically:
     *   1. Marks booking Completed with fee
     *   2. Frees the parking slot
     *   3. Updates payment to Paid
     */
    public double processExit(int bookingId) throws SQLException {
        Connection conn = DBConnection.getConnection();
        conn.setAutoCommit(false);
        try {
            // 1. Get entry_time and slot_id
            String fetch = "SELECT slot_id, entry_time FROM bookings WHERE id = ? AND status = 'Active'";
            int slotId;
            long entryMillis;
            try (PreparedStatement ps = conn.prepareStatement(fetch)) {
                ps.setInt(1, bookingId);
                try (ResultSet rs = ps.executeQuery()) {
                    if (!rs.next()) throw new SQLException("Booking not found or already completed");
                    slotId      = rs.getInt("slot_id");
                    entryMillis = rs.getTimestamp("entry_time").getTime();
                }
            }

            // 2. Calculate fee  (₹50 per hour, minimum 1 hour)
            long hours = Math.max(1, (long) Math.ceil((System.currentTimeMillis() - entryMillis) / 3_600_000.0));
            double fee = hours * 50.0;

            // 3. Update bookings
            try (PreparedStatement ps = conn.prepareStatement(
                    "UPDATE bookings SET exit_time = NOW(), total_fee = ?, status = 'Completed' WHERE id = ?")) {
                ps.setDouble(1, fee);
                ps.setInt(2, bookingId);
                ps.executeUpdate();
            }

            // 4. Free the parking slot
            try (PreparedStatement ps = conn.prepareStatement(
                    "UPDATE parking_slots SET status = 'Available' WHERE id = ?")) {
                ps.setInt(1, slotId);
                ps.executeUpdate();
            }

            // 5. Mark payment Paid
            try (PreparedStatement ps = conn.prepareStatement(
                    "UPDATE payments SET amount = ?, payment_date = NOW(), status = 'Paid' WHERE booking_id = ?")) {
                ps.setDouble(1, fee);
                ps.setInt(2, bookingId);
                ps.executeUpdate();
            }

            conn.commit();
            return fee;

        } catch (SQLException e) {
            conn.rollback();
            throw e;
        } finally {
            conn.setAutoCommit(true);
            conn.close();
        }
    }

    public int countActive() throws SQLException {
        String sql = "SELECT COUNT(*) FROM bookings WHERE status = 'Active'";
        try (Connection conn = DBConnection.getConnection();
             Statement  stmt = conn.createStatement();
             ResultSet  rs   = stmt.executeQuery(sql)) {
            return rs.next() ? rs.getInt(1) : 0;
        }
    }

    private Booking map(ResultSet rs) throws SQLException {
        Booking b = new Booking();
        b.id             = rs.getInt("id");
        b.user_id        = rs.getInt("user_id");
        b.user_name      = rs.getString("user_name");
        b.vehicle        = rs.getString("vehicle");
        b.vehicle_type   = rs.getString("vehicle_type");
        b.slot_id        = rs.getInt("slot_id");
        b.slot_floor     = rs.getInt("slot_floor");
        b.entry_time     = rs.getString("entry_time");
        b.exit_time      = rs.getString("exit_time");
        b.total_fee      = rs.getDouble("total_fee");
        b.status         = rs.getString("status");
        b.payment_status = rs.getString("payment_status");
        return b;
    }
}
