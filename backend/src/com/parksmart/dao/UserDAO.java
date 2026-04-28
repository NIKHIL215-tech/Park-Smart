package com.parksmart.dao;

import com.parksmart.DBConnection;
import com.parksmart.model.User;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class UserDAO {

    public List<User> getAllUsers() throws SQLException {
        List<User> list = new ArrayList<>();
        String sql = "SELECT id, name, email, phone FROM users ORDER BY id";

        try (Connection conn = DBConnection.getConnection();
             Statement  stmt = conn.createStatement();
             ResultSet  rs   = stmt.executeQuery(sql)) {

            while (rs.next()) list.add(map(rs));
        }
        return list;
    }

    public User login(String email, String password) throws SQLException {
        String sql = "SELECT id, name, email, phone FROM users WHERE email = ? AND password = ?";

        try (Connection      conn = DBConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setString(1, email);
            ps.setString(2, password);

            try (ResultSet rs = ps.executeQuery()) {
                return rs.next() ? map(rs) : null;
            }
        }
    }

    public boolean emailExists(String email) throws SQLException {
        String sql = "SELECT 1 FROM users WHERE email = ?";

        try (Connection      conn = DBConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {

            ps.setString(1, email);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next();
            }
        }
    }

    public int register(User u) throws SQLException {
        String sql = "INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)";

        try (Connection      conn = DBConnection.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {

            ps.setString(1, u.name);
            ps.setString(2, u.email);
            ps.setString(3, u.phone);
            ps.setString(4, u.password);
            ps.executeUpdate();

            try (ResultSet keys = ps.getGeneratedKeys()) {
                return keys.next() ? keys.getInt(1) : -1;
            }
        }
    }

    private User map(ResultSet rs) throws SQLException {
        User u = new User();
        u.id    = rs.getInt("id");
        u.name  = rs.getString("name");
        u.email = rs.getString("email");
        u.phone = rs.getString("phone");
        return u;
    }
}
