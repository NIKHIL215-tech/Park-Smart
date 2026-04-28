package com.parksmart.model;

public class Booking {
    public int    id;
    public int    user_id;
    public String user_name;      // populated via JOIN
    public String vehicle;
    public String vehicle_type;
    public int    slot_id;
    public int    slot_floor;     // populated via JOIN
    public String entry_time;
    public String exit_time;
    public double total_fee;
    public String status;
    public String payment_status; // populated via JOIN

    public String toJson() {
        return "{"
            + "\"id\":"             + id                          + ","
            + "\"user_id\":"        + user_id                     + ","
            + "\"user_name\":"      + q(user_name)                + ","
            + "\"vehicle\":"        + q(vehicle)                  + ","
            + "\"vehicle_type\":"   + q(vehicle_type)             + ","
            + "\"slot_id\":"        + slot_id                     + ","
            + "\"slot_floor\":"     + slot_floor                  + ","
            + "\"entry_time\":"     + q(entry_time)               + ","
            + "\"exit_time\":"      + (exit_time == null ? "null" : q(exit_time)) + ","
            + "\"total_fee\":"      + total_fee                   + ","
            + "\"status\":"         + q(status)                   + ","
            + "\"payment_status\":" + q(payment_status)
            + "}";
    }

    private static String q(String s) {
        if (s == null) return "null";
        return "\"" + s.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }
}
