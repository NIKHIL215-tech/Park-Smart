package com.parksmart.model;

public class User {
    public int    id;
    public String name;
    public String email;
    public String phone;
    public String password;

    public String toJson() {
        return "{"
            + "\"id\":"     + id           + ","
            + "\"name\":"   + q(name)      + ","
            + "\"email\":"  + q(email)     + ","
            + "\"phone\":"  + q(phone)
            + "}";
    }

    private static String q(String s) {
        if (s == null) return "null";
        return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }
}
