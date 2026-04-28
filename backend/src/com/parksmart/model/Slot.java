package com.parksmart.model;

public class Slot {
    public int    id;
    public int    floor;
    public String type;
    public String status;

    public String toJson() {
        return "{"
            + "\"id\":"     + id        + ","
            + "\"floor\":"  + floor     + ","
            + "\"type\":"   + q(type)   + ","
            + "\"status\":" + q(status)
            + "}";
    }

    private static String q(String s) {
        if (s == null) return "null";
        return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }
}
