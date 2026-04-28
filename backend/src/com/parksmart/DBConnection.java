package com.parksmart;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * JDBC Connection helper.
 *
 * JDBC URL format:
 *   jdbc:mysql://<host>:<port>/<database>?serverTimezone=UTC
 *
 * Change DB_USER and DB_PASS to match your MySQL installation.
 */
public class DBConnection {

    private static final String DB_URL  = "jdbc:mysql://localhost:3306/parksmart?serverTimezone=UTC";
    private static final String DB_USER = "root";
    private static final String DB_PASS = "cseBtech4202";

    static {
        try {
            // Explicitly load the MySQL JDBC driver (required for older JDBC versions)
            Class.forName("com.mysql.cj.jdbc.Driver");
            System.out.println("[JDBC] Driver loaded: com.mysql.cj.jdbc.Driver");
        } catch (ClassNotFoundException e) {
            System.err.println("[JDBC] ERROR: MySQL Connector/J jar not found in lib/");
            throw new RuntimeException(e);
        }
    }

    /** Returns a new JDBC Connection from the MySQL DriverManager. */
    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);
    }
}
