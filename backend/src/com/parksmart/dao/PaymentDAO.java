package com.parksmart.dao;

import com.parksmart.DBConnection;

import java.sql.*;

public class PaymentDAO {

    public boolean createPending(int bookingId) throws SQLException {
        String sql = "INSERT INTO payments (booking_id, amount, payment_date, status) VALUES (?, 0, NOW(), 'Pending')";

        try (Connection      conn = DBConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setInt(1, bookingId);
            return ps.executeUpdate() > 0;
        }
    }

    public double getTotalRevenue() throws SQLException {
        String sql = "SELECT COALESCE(SUM(amount), 0) AS total FROM payments WHERE status = 'Paid'";

        try (Connection conn = DBConnection.getConnection();
             Statement  stmt = conn.createStatement();
             ResultSet  rs   = stmt.executeQuery(sql)) {

            return rs.next() ? rs.getDouble("total") : 0;
        }
    }
}
