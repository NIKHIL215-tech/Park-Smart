package com.parksmart.dao;

import com.parksmart.DBConnection;
import com.parksmart.model.Slot;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class SlotDAO {

    public List<Slot> getAllSlots(Integer floor) throws SQLException {
        List<Slot> list = new ArrayList<>();
        String sql = (floor != null)
                ? "SELECT * FROM parking_slots WHERE floor = ? ORDER BY id"
                : "SELECT * FROM parking_slots ORDER BY id";

        try (Connection conn = DBConnection.getConnection()) {
            ResultSet rs;
            if (floor != null) {
                PreparedStatement ps = conn.prepareStatement(sql);
                ps.setInt(1, floor);
                rs = ps.executeQuery();
            } else {
                rs = conn.createStatement().executeQuery(sql);
            }
            while (rs.next()) list.add(map(rs));
            rs.close();
        }
        return list;
    }

    public Slot getById(int id) throws SQLException {
        String sql = "SELECT * FROM parking_slots WHERE id = ?";

        try (Connection      conn = DBConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setInt(1, id);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? map(rs) : null;
            }
        }
    }

    public boolean addSlot(int floor, String type) throws SQLException {
        String sql = "INSERT INTO parking_slots (floor, type, status) VALUES (?, ?, 'Available')";

        try (Connection      conn = DBConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setInt(1, floor);
            ps.setString(2, type);
            return ps.executeUpdate() > 0;
        }
    }

    public boolean updateStatus(int slotId, String status) throws SQLException {
        String sql = "UPDATE parking_slots SET status = ? WHERE id = ?";

        try (Connection      conn = DBConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setString(1, status);
            ps.setInt(2, slotId);
            return ps.executeUpdate() > 0;
        }
    }

    public int countAvailable() throws SQLException {
        String sql = "SELECT COUNT(*) FROM parking_slots WHERE status = 'Available'";
        try (Connection conn = DBConnection.getConnection();
             Statement  stmt = conn.createStatement();
             ResultSet  rs   = stmt.executeQuery(sql)) {
            return rs.next() ? rs.getInt(1) : 0;
        }
    }

    public int countOccupied() throws SQLException {
        String sql = "SELECT COUNT(*) FROM parking_slots WHERE status = 'Occupied'";
        try (Connection conn = DBConnection.getConnection();
             Statement  stmt = conn.createStatement();
             ResultSet  rs   = stmt.executeQuery(sql)) {
            return rs.next() ? rs.getInt(1) : 0;
        }
    }

    private Slot map(ResultSet rs) throws SQLException {
        Slot s = new Slot();
        s.id     = rs.getInt("id");
        s.floor  = rs.getInt("floor");
        s.type   = rs.getString("type");
        s.status = rs.getString("status");
        return s;
    }
}
