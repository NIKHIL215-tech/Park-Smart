from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ── Page margins ────────────────────────────────────────────────────────────
for section in doc.sections:
    section.top_margin    = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin   = Cm(2.5)
    section.right_margin  = Cm(2.5)

# ── Colour palette ───────────────────────────────────────────────────────────
NAVY      = RGBColor(0x0d, 0x1b, 0x2a)
TEAL      = RGBColor(0x00, 0xb4, 0x8a)
BLUE      = RGBColor(0x2b, 0x6c, 0xb0)
ORANGE    = RGBColor(0xd6, 0x9e, 0x2e)
GREEN     = RGBColor(0x27, 0x67, 0x49)
LIGHT_BG  = RGBColor(0xf0, 0xf4, 0xf8)
GREY      = RGBColor(0x71, 0x80, 0x96)
BLACK     = RGBColor(0x0d, 0x1b, 0x2a)
CODE_BG   = RGBColor(0x0d, 0x1b, 0x2a)
CODE_TEXT = RGBColor(0xe2, 0xe8, 0xf0)
SPEAK_BG  = RGBColor(0xe6, 0xf7, 0xf0)
SPEAK_TXT = RGBColor(0x27, 0x67, 0x49)
NOTE_BG   = RGBColor(0xff, 0xfb, 0xeb)
NOTE_TXT  = RGBColor(0x74, 0x42, 0x10)
WHITE     = RGBColor(0xff, 0xff, 0xff)

# ── Helpers ──────────────────────────────────────────────────────────────────
def shade_cell(cell, rgb: RGBColor):
    hex_color = str(rgb)  # RGBColor is a str subclass, already in RRGGBB hex
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tcPr.append(shd)

def set_cell_border(cell, **kwargs):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top','left','bottom','right'):
        if edge in kwargs:
            el = OxmlElement(f'w:{edge}')
            el.set(qn('w:val'),  kwargs[edge].get('val',  'single'))
            el.set(qn('w:sz'),   str(kwargs[edge].get('sz',  4)))
            el.set(qn('w:space'),'0')
            el.set(qn('w:color'),kwargs[edge].get('color','auto'))
            tcBorders.append(el)
    tcPr.append(tcBorders)

def no_space_before(para):
    pPr = para._p.get_or_add_pPr()
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:before'), '0')
    spacing.set(qn('w:after'),  '60')
    pPr.append(spacing)

def add_heading(text, level=1, color=NAVY):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18 if level == 1 else 12)
    p.paragraph_format.space_after  = Pt(6)
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(18 if level == 1 else 14 if level == 2 else 12)
    run.font.color.rgb = color
    return p

def add_body(text, bold_parts=None, indent=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(6)
    if indent:
        p.paragraph_format.left_indent = Cm(0.6)
    run = p.add_run(text)
    run.font.size      = Pt(10.5)
    run.font.color.rgb = RGBColor(0x2d, 0x3d, 0x50)
    return p

def add_bullet(text, color=NAVY):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after  = Pt(3)
    p.paragraph_format.left_indent  = Cm(0.8)
    run = p.add_run(text)
    run.font.size      = Pt(10.5)
    run.font.color.rgb = RGBColor(0x2d, 0x3d, 0x50)
    return p

def add_code_block(title, filename, lines):
    # Header row
    t = doc.add_table(rows=2, cols=1)
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    # header cell
    hdr = t.rows[0].cells[0]
    shade_cell(hdr, RGBColor(0x1a, 0x3c, 0x5e))
    hp = hdr.paragraphs[0]
    hp.clear()
    hp.paragraph_format.space_before = Pt(3)
    hp.paragraph_format.space_after  = Pt(3)
    r1 = hp.add_run(f'  {title}')
    r1.font.size      = Pt(9)
    r1.font.color.rgb = RGBColor(0xaa, 0xcc, 0xee)
    r1.font.italic    = True
    r2 = hp.add_run(f'   [{filename}]')
    r2.font.size      = Pt(9)
    r2.font.color.rgb = TEAL
    r2.bold           = True
    # code cell
    code = t.rows[1].cells[0]
    shade_cell(code, CODE_BG)
    cp = code.paragraphs[0]
    cp.clear()
    cp.paragraph_format.space_before = Pt(6)
    cp.paragraph_format.space_after  = Pt(6)
    cp.paragraph_format.left_indent  = Cm(0.4)
    for line in lines:
        r = cp.add_run(line + '\n')
        r.font.name       = 'Courier New'
        r.font.size       = Pt(8.5)
        r.font.color.rgb  = CODE_TEXT
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_speak_box(text):
    t = doc.add_table(rows=1, cols=1)
    t.style = 'Table Grid'
    c = t.rows[0].cells[0]
    shade_cell(c, RGBColor(0xe8, 0xf5, 0xf1))
    set_cell_border(c,
        top    ={'val':'single','sz':8,'color':'9AE6C0'},
        left   ={'val':'single','sz':8,'color':'9AE6C0'},
        bottom ={'val':'single','sz':8,'color':'9AE6C0'},
        right  ={'val':'single','sz':8,'color':'9AE6C0'})
    p = c.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.left_indent  = Cm(0.3)
    r1 = p.add_run('🎤  SAY THIS:  ')
    r1.bold           = True
    r1.font.size      = Pt(8)
    r1.font.color.rgb = RGBColor(0x0f, 0x6e, 0x56)
    r2 = p.add_run(f'"{text}"')
    r2.italic         = True
    r2.font.size      = Pt(10.5)
    r2.font.color.rgb = SPEAK_TXT
    doc.add_paragraph().paragraph_format.space_after = Pt(3)

def add_note_box(text):
    t = doc.add_table(rows=1, cols=1)
    t.style = 'Table Grid'
    c = t.rows[0].cells[0]
    shade_cell(c, RGBColor(0xff, 0xfb, 0xeb))
    set_cell_border(c,
        top   ={'val':'single','sz':8,'color':'F6E05E'},
        left  ={'val':'single','sz':8,'color':'F6E05E'},
        bottom={'val':'single','sz':8,'color':'F6E05E'},
        right ={'val':'single','sz':8,'color':'F6E05E'})
    p = c.paragraphs[0]
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(4)
    p.paragraph_format.left_indent  = Cm(0.3)
    r1 = p.add_run('📝  NOTE:  ')
    r1.bold           = True
    r1.font.size      = Pt(8)
    r1.font.color.rgb = RGBColor(0x74, 0x42, 0x10)
    r2 = p.add_run(text)
    r2.font.size      = Pt(10.5)
    r2.font.color.rgb = NOTE_TXT
    doc.add_paragraph().paragraph_format.space_after = Pt(3)

def section_divider():
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after  = Pt(10)
    pPr = p._p.get_or_add_pPr()
    pb = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'),   'single')
    bottom.set(qn('w:sz'),    '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'E2E8F0')
    pb.append(bottom)
    pPr.append(pb)

# ═══════════════════════════════════════════════════════════════════════════
#  COVER PAGE
# ═══════════════════════════════════════════════════════════════════════════
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(40)
r = p.add_run('🅿  ParkSmart')
r.font.size      = Pt(32)
r.font.color.rgb = NAVY
r.bold           = True

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run('Intelligent Parking Space Management System')
r.font.size      = Pt(16)
r.font.color.rgb = TEAL
r.bold           = True

doc.add_paragraph()

# info table
t = doc.add_table(rows=5, cols=2)
t.alignment = WD_TABLE_ALIGNMENT.CENTER
t.style     = 'Table Grid'
rows_data = [
    ('Project Type', 'DBMS Mini Project — 3-Tier Web Application'),
    ('Institute',    'SRM Institute of Science and Technology'),
    ('Tech Stack',   'Java (Backend) + MySQL (Database) + HTML/CSS/JS (Frontend)'),
    ('Connectivity', 'JDBC — Java Database Connectivity'),
    ('Server',       'localhost:8080  |  DB: parksmart @ localhost:3306'),
]
for i, (k, v) in enumerate(rows_data):
    row = t.rows[i]
    shade_cell(row.cells[0], RGBColor(0x0d, 0x1b, 0x2a))
    shade_cell(row.cells[1], RGBColor(0xf7, 0xfa, 0xfc))
    row.cells[0].paragraphs[0].clear()
    rk = row.cells[0].paragraphs[0].add_run(k)
    rk.bold = True; rk.font.size = Pt(10); rk.font.color.rgb = WHITE
    row.cells[1].paragraphs[0].clear()
    rv = row.cells[1].paragraphs[0].add_run(v)
    rv.font.size = Pt(10); rv.font.color.rgb = NAVY

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 1 — PROJECT OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════
add_heading('1.  Project Overview & Architecture', 1)

add_body(
    'ParkSmart is a 3-tier client-server application. Each tier is a separate folder with a '
    'clear, single responsibility. The tiers never skip each other — the browser never talks '
    'directly to MySQL.'
)

add_heading('Architecture Flow', 2, BLUE)
add_code_block('3-Tier Data Flow', 'architecture',
[
    'Browser (frontend/)   --HTTP fetch()-->   Java Server (port 8080)   --JDBC-->   MySQL (parksmart)',
    '',
    'Tier 1  |  frontend/           HTML, CSS, JavaScript (runs in browser)',
    'Tier 2  |  backend/src/        Java — receives HTTP requests, runs SQL, returns JSON',
    'Tier 3  |  database/           MySQL — all data stored here permanently',
])

add_heading('File Structure', 2, BLUE)
add_code_block('Complete project layout', 'ParkSmart/',
[
    'ParkSmart/',
    '├── database/',
    '│   └── schema.sql          ← DDL (CREATE TABLE) + DML seed data',
    '├── backend/',
    '│   ├── src/com/parksmart/',
    '│   │   ├── Main.java           ← Starts HTTP server on port 8080',
    '│   │   ├── DBConnection.java   ← JDBC connection (the bridge to MySQL)',
    '│   │   ├── model/              ← User.java, Slot.java, Booking.java',
    '│   │   ├── dao/                ← UserDAO, SlotDAO, BookingDAO, PaymentDAO',
    '│   │   └── handler/ApiHandler.java  ← Routes HTTP requests to DAOs',
    '│   ├── lib/mysql-connector-j-8.4.0.jar',
    '│   ├── compile.bat             ← Compiles all Java files',
    '│   └── run.bat                 ← Starts the server',
    '└── frontend/',
    '    ├── index.html              ← Same UI, HTML structure only',
    '    ├── style.css               ← All CSS styling',
    '    └── app.js                  ← All JS logic using fetch()',
])

section_divider()

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 2 — JDBC CONNECTIVITY
# ═══════════════════════════════════════════════════════════════════════════
add_heading('2.  How JDBC Database Connectivity Works', 1)

add_body(
    'JDBC (Java Database Connectivity) is a standard Java API that allows Java programs to '
    'connect to any relational database. It works through a driver JAR file that translates '
    'Java method calls into the database\'s binary wire protocol.'
)

add_heading('Step-by-Step JDBC Flow', 2, BLUE)
steps = [
    ('Step 1 — Load the Driver',
     'Class.forName("com.mysql.cj.jdbc.Driver") registers the MySQL JDBC driver with the JVM. '
     'Done once at server startup. The driver JAR (mysql-connector-j-8.4.0.jar) must be in the classpath.'),
    ('Step 2 — Open a Connection',
     'DriverManager.getConnection(URL, user, pass) opens a TCP socket to MySQL on port 3306, '
     'authenticates, and returns a Connection object. Every query needs one.'),
    ('Step 3 — Create a PreparedStatement',
     'PreparedStatement is used for queries with parameters (?, ?, ...). '
     'The ? placeholders are filled with setString(), setInt(), etc. '
     'This prevents SQL injection — user input can never break the query structure.'),
    ('Step 4 — Execute SQL',
     'executeQuery() for SELECT — returns a ResultSet. '
     'executeUpdate() for INSERT / UPDATE / DELETE — returns rows affected count.'),
    ('Step 5 — Read the ResultSet',
     'rs.next() moves to the next row. rs.getString("col"), rs.getInt("col") etc. read column values. '
     'Loop until rs.next() returns false.'),
    ('Step 6 — Close Everything',
     'try-with-resources (try (Connection conn = ...)) auto-closes Connection, PreparedStatement, '
     'and ResultSet. Prevents connection leaks.'),
]
for title, desc in steps:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after  = Pt(2)
    p.paragraph_format.left_indent  = Cm(0.3)
    r1 = p.add_run(f'  {title}: ')
    r1.bold = True; r1.font.size = Pt(10.5); r1.font.color.rgb = NAVY
    r2 = p.add_run(desc)
    r2.font.size = Pt(10.5); r2.font.color.rgb = RGBColor(0x4a, 0x55, 0x68)

doc.add_paragraph()

add_heading('DBConnection.java — The JDBC Bridge', 2, BLUE)
add_code_block('Full JDBC connection code', 'DBConnection.java',
[
    'public class DBConnection {',
    '',
    '    // JDBC URL: jdbc:mysql://<host>:<port>/<database>',
    '    private static final String DB_URL  = "jdbc:mysql://localhost:3306/parksmart?serverTimezone=UTC";',
    '    private static final String DB_USER = "root";',
    '    private static final String DB_PASS = "cseBtech4202";',
    '',
    '    static {',
    '        // Step 1 — register MySQL driver with the JVM (runs once on startup)',
    '        Class.forName("com.mysql.cj.jdbc.Driver");',
    '        System.out.println("[JDBC] Driver loaded: com.mysql.cj.jdbc.Driver");',
    '    }',
    '',
    '    // Step 2 — open a fresh JDBC connection for every query',
    '    public static Connection getConnection() throws SQLException {',
    '        return DriverManager.getConnection(DB_URL, DB_USER, DB_PASS);',
    '    }',
    '}',
])

add_heading('UserDAO.java — Complete JDBC Query Cycle (Login)', 2, BLUE)
add_code_block('PreparedStatement + ResultSet example', 'UserDAO.java',
[
    'public User login(String email, String password) throws SQLException {',
    '',
    '    String sql = "SELECT id, name, email FROM users WHERE email = ? AND password = ?";',
    '    //                                                          ^ placeholder for safe input',
    '',
    '    // try-with-resources: auto-closes conn, ps, rs when block ends',
    '    try (Connection       conn = DBConnection.getConnection();    // Step 2',
    '         PreparedStatement ps  = conn.prepareStatement(sql)) {   // Step 3',
    '',
    '        ps.setString(1, email);     // fill 1st ?',
    '        ps.setString(2, password);  // fill 2nd ?',
    '',
    '        try (ResultSet rs = ps.executeQuery()) {  // Step 4 — run SELECT',
    '            if (rs.next()) {                       // Step 5 — read row',
    '                User u  = new User();',
    '                u.id    = rs.getInt("id");',
    '                u.name  = rs.getString("name");',
    '                u.email = rs.getString("email");',
    '                return u;',
    '            }',
    '        }',
    '    }                              // Step 6 — auto-closed here',
    '    return null;  // login failed',
    '}',
])

add_heading('BookingDAO.java — JDBC Transaction (Exit Processing)', 2, BLUE)
add_body(
    'When a vehicle exits, three tables must update atomically. '
    'If any one fails, all three must roll back. This uses a JDBC Transaction.'
)
add_code_block('Transaction: commit() / rollback()', 'BookingDAO.java',
[
    'Connection conn = DBConnection.getConnection();',
    'conn.setAutoCommit(false);  // START TRANSACTION — nothing written until commit()',
    'try {',
    '    // 1. Mark booking as Completed, set exit_time and total_fee',
    '    UPDATE bookings SET exit_time=NOW(), total_fee=?, status="Completed" WHERE id=?',
    '',
    '    // 2. Free the parking slot',
    '    UPDATE parking_slots SET status="Available" WHERE id=?',
    '',
    '    // 3. Mark payment as Paid',
    '    UPDATE payments SET amount=?, status="Paid" WHERE booking_id=?',
    '',
    '    conn.commit();   // ALL 3 succeeded — write permanently to DB',
    '',
    '} catch (SQLException e) {',
    '    conn.rollback(); // ANY failure — undo everything, data stays consistent',
    '    throw e;',
    '}',
    '// This guarantees ACID: Atomicity, Consistency, Isolation, Durability',
])

section_divider()

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 3 — CODE EXPLANATION
# ═══════════════════════════════════════════════════════════════════════════
add_heading('3.  File-by-File Code Explanation', 1)

add_heading('Main.java — HTTP Server Entry Point', 2, BLUE)
add_body(
    'Uses Java\'s built-in com.sun.net.httpserver.HttpServer — no external server like Tomcat '
    'or Spring needed. Sets up two contexts: one for API routes, one for static HTML/CSS/JS files.'
)
add_code_block('Server setup', 'Main.java',
[
    'HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);',
    'server.createContext("/api/", new ApiHandler());    // /api/* → business logic',
    'server.createContext("/",     new StaticHandler()); // /* → serve frontend files',
    'server.setExecutor(Executors.newFixedThreadPool(4)); // 4 threads',
    'server.start();',
    '// Result: http://localhost:8080 serves the full app',
])

add_heading('ApiHandler.java — Request Router', 2, BLUE)
add_body(
    'One class handles all /api/* requests. Reads the HTTP method and path, calls the '
    'correct DAO method, and writes a JSON response. Also adds CORS headers for browser compatibility.'
)
add_code_block('Route handling logic', 'ApiHandler.java',
[
    '// Incoming: GET /api/slots?floor=2',
    '// ↓ parse path + query string',
    '// ↓ call slotDAO.getAllSlots(2)',
    '// ↓ convert List<Slot> → JSON string',
    '// ↓ write HTTP 200 response',
    '',
    '// Incoming: POST /api/bookings  { vehicle:"TN01AB", slot_id:3 }',
    '// ↓ read JSON body',
    '// ↓ check slot is Available via slotDAO',
    '// ↓ bookingDAO.createBooking()',
    '// ↓ paymentDAO.createPending()',
    '// ↓ slotDAO.updateStatus(3, "Occupied")',
    '// ↓ return { "success":true, "booking_id":4 }',
])

add_heading('DAO Layer — Data Access Objects', 2, BLUE)
add_body(
    'Each database table has its own DAO class. All SQL queries are isolated here. '
    'The handler layer never writes SQL directly — it only calls DAO methods.'
)
add_code_block('DAO structure and JOIN query example', 'dao/',
[
    'UserDAO.java    → SQL on users table (login, register, list)',
    'SlotDAO.java    → SQL on parking_slots (list, add, update status)',
    'BookingDAO.java → SQL on bookings (create, list, exit) — 4-table JOIN',
    'PaymentDAO.java → SQL on payments (create pending, mark paid, sum revenue)',
    '',
    '// BookingDAO uses a JOIN query so one DB call returns all needed data:',
    'SELECT b.id, u.name AS user_name, b.vehicle,',
    '       ps.floor AS slot_floor, b.status, p.status AS payment_status',
    'FROM bookings b',
    'LEFT JOIN users         u  ON b.user_id    = u.id',
    'LEFT JOIN parking_slots ps ON b.slot_id    = ps.id',
    'LEFT JOIN payments      p  ON p.booking_id = b.id',
    'ORDER BY b.entry_time DESC',
])

add_heading('app.js — Frontend Logic (fetch instead of in-memory DB)', 2, BLUE)
add_code_block('How the frontend gets live data from MySQL', 'frontend/app.js',
[
    '// OLD (single HTML file): hardcoded data in a JS object in RAM',
    '// const DB = { users:[...], slots:[...], bookings:[...] }',
    '',
    '// NEW (3-tier): every page load fires a real HTTP request to Java → MySQL',
    'async function loadHome() {',
    '    const [stats, slots] = await Promise.all([',
    "        fetch('/api/stats').then(r => r.json()),",
    "        fetch('/api/slots').then(r => r.json())",
    '    ]);',
    '    // stats = { avail:6, occupied:2, active:1, revenue:250 }  ← live from MySQL',
    '    // slots = [{ id:1, floor:1, type:"Car", status:"Available"}, ...]',
    "    document.getElementById('homeAvail').textContent = stats.avail;",
    '    // ... render slot cards from real database data',
    '}',
])

section_divider()

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 4 — LIVE DML DEMO
# ═══════════════════════════════════════════════════════════════════════════
add_heading('4.  Live DML Demo — Change Database, See it in the App', 1)

add_body(
    'Run any of these SQL commands in MySQL Workbench (connected to the parksmart database), '
    'then refresh http://localhost:8080 in the browser. The UI reflects every change instantly '
    'because every page load runs a fresh SQL query — there is no cached or hardcoded data.'
)

add_note_box(
    'Open MySQL Workbench → Local Instance → password: cseBtech4202 → '
    'click "parksmart" in the left panel → open a new query tab → paste and run.'
)

# DML table
headers = ['What to Show', 'SQL Command to Run', 'Where it Appears in the App']
rows = [
    ('Free an occupied slot',
     'UPDATE parking_slots\nSET status = \'Available\'\nWHERE id = 3;',
     'Home page: slot S3 turns green. Available Slots count increases by 1.'),
    ('Add a new parking slot',
     'INSERT INTO parking_slots (floor, type, status)\nVALUES (4, \'Car\', \'Available\');',
     'Home map: new slot S9 appears. Booking page: Floor 4 filter pill appears.'),
    ('Add a new user',
     'INSERT INTO users (name, email, phone, password)\nVALUES (\'Test User\', \'test@gmail.com\', \'9000011111\', \'test@123\');',
     'Admin page: Total Users count increases. Users table shows new row.'),
    ('Delete a booking',
     'DELETE FROM bookings WHERE id = 2;',
     'Admin page: booking row disappears. Active Bookings count drops.'),
    ('Change a slot type',
     'UPDATE parking_slots SET type = \'Bike\'\nWHERE id = 1;',
     'Home map: slot S1 badge changes Car → Bike. Booking page reflects it.'),
    ('Manually complete a booking',
     'UPDATE bookings\nSET status=\'Completed\', total_fee=200, exit_time=NOW()\nWHERE id=2;\nUPDATE payments\nSET status=\'Paid\', amount=200\nWHERE booking_id=2;',
     'My Bookings: booking shows Completed. Revenue on Home/Admin increases by ₹200.'),
    ('View 4-table JOIN (same query the Admin page uses)',
     'SELECT b.id, u.name, b.vehicle,\n       ps.floor, b.status, p.status AS paid\nFROM bookings b\nJOIN users u ON b.user_id=u.id\nJOIN parking_slots ps ON b.slot_id=ps.id\nJOIN payments p ON p.booking_id=b.id;',
     'This is the raw SQL behind the Admin Bookings table. Shows all 4 tables joined.'),
    ('Check total revenue',
     'SELECT SUM(amount) AS total_revenue\nFROM payments\nWHERE status = \'Paid\';',
     'Should exactly match the Revenue card on Home and Admin pages.'),
]

t = doc.add_table(rows=1 + len(rows), cols=3)
t.style     = 'Table Grid'
t.alignment = WD_TABLE_ALIGNMENT.LEFT

# header row
for i, h in enumerate(headers):
    cell = t.rows[0].cells[i]
    shade_cell(cell, NAVY)
    p = cell.paragraphs[0]
    p.clear()
    r = p.add_run(h)
    r.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = WHITE

# data rows
for ri, (what, sql, effect) in enumerate(rows):
    row = t.rows[ri + 1]
    shade_cell(row.cells[0], RGBColor(0xf7, 0xfa, 0xfc) if ri % 2 == 0 else WHITE)
    shade_cell(row.cells[1], RGBColor(0x0d, 0x1b, 0x2a))
    shade_cell(row.cells[2], RGBColor(0xf0, 0xf4, 0xf8) if ri % 2 == 0 else WHITE)

    p0 = row.cells[0].paragraphs[0]; p0.clear()
    r0 = p0.add_run(what); r0.bold = True; r0.font.size = Pt(9.5); r0.font.color.rgb = NAVY

    p1 = row.cells[1].paragraphs[0]; p1.clear()
    r1 = p1.add_run(sql)
    r1.font.name = 'Courier New'; r1.font.size = Pt(8); r1.font.color.rgb = TEAL

    p2 = row.cells[2].paragraphs[0]; p2.clear()
    r2 = p2.add_run(effect); r2.font.size = Pt(9); r2.font.color.rgb = RGBColor(0x4a, 0x55, 0x68)

doc.add_paragraph()
add_speak_box(
    'Sir, you can see — when I run this UPDATE directly in MySQL Workbench and refresh the browser, '
    'the UI shows the new data immediately. Every page load fires a fresh JDBC query to MySQL. '
    'There is no cache and no hardcoded data in the frontend.'
)

section_divider()

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 5 — DDL
# ═══════════════════════════════════════════════════════════════════════════
add_heading('5.  DDL — Database Schema', 1)
add_body(
    'Four tables with primary keys, foreign keys, ENUM constraints, and referential integrity rules. '
    'The schema is in database/schema.sql and was created using CREATE TABLE statements.'
)

add_code_block('Complete DDL — all four tables', 'database/schema.sql',
[
    '-- TABLE 1: users — stores login accounts',
    'CREATE TABLE users (',
    '    id       INT AUTO_INCREMENT PRIMARY KEY,',
    '    name     VARCHAR(100) NOT NULL,',
    '    email    VARCHAR(100) NOT NULL UNIQUE,   -- no duplicate emails',
    '    phone    VARCHAR(15),',
    '    password VARCHAR(100) NOT NULL',
    ');',
    '',
    '-- TABLE 2: parking_slots — the physical parking spaces',
    'CREATE TABLE parking_slots (',
    '    id     INT AUTO_INCREMENT PRIMARY KEY,',
    '    floor  INT                          NOT NULL,',
    "    type   ENUM('Car','Bike')           NOT NULL,  -- only these 2 values allowed",
    "    status ENUM('Available','Occupied') NOT NULL DEFAULT 'Available'",
    ');',
    '',
    '-- TABLE 3: bookings — who parked where and when',
    'CREATE TABLE bookings (',
    '    id           INT AUTO_INCREMENT PRIMARY KEY,',
    '    user_id      INT,',
    '    vehicle      VARCHAR(20)               NOT NULL,',
    "    vehicle_type ENUM('Car','Bike')         NOT NULL,",
    '    slot_id      INT,',
    '    entry_time   DATETIME                  DEFAULT CURRENT_TIMESTAMP,',
    '    exit_time    DATETIME                  NULL,        -- NULL = still parked',
    '    total_fee    DECIMAL(10,2)             DEFAULT 0,',
    "    status       ENUM('Active','Completed') DEFAULT 'Active',",
    '    FOREIGN KEY (user_id) REFERENCES users(id)         ON DELETE SET NULL,',
    '    FOREIGN KEY (slot_id) REFERENCES parking_slots(id) ON DELETE SET NULL',
    ');',
    '',
    '-- TABLE 4: payments — billing record per booking',
    'CREATE TABLE payments (',
    '    id           INT AUTO_INCREMENT PRIMARY KEY,',
    '    booking_id   INT,',
    '    amount       DECIMAL(10,2)       DEFAULT 0,',
    '    payment_date DATETIME            DEFAULT CURRENT_TIMESTAMP,',
    "    status       ENUM('Pending','Paid') DEFAULT 'Pending',",
    '    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE',
    ');',
])

add_speak_box(
    'Sir, I have used ENUM for status and type columns to enforce data integrity at the MySQL level — '
    'the database itself will reject any invalid value. Foreign keys ensure referential integrity — '
    'a booking cannot reference a user or slot that does not exist. '
    'ON DELETE SET NULL and ON DELETE CASCADE control what happens when a referenced record is deleted.'
)

section_divider()

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 6 — API ROUTES
# ═══════════════════════════════════════════════════════════════════════════
add_heading('6.  REST API Routes Reference', 1)
add_body(
    'The Java server exposes 11 endpoints. The browser calls them using fetch(). '
    'You can test GET routes directly in the browser at http://localhost:8080/api/...'
)

api_headers = ['Method', 'URL', 'What it Does', 'SQL Used']
api_rows = [
    ('GET',  '/api/stats',           'Dashboard counts + revenue',        'COUNT() + SUM() queries'),
    ('GET',  '/api/slots',           'All parking slots',                  'SELECT * FROM parking_slots'),
    ('GET',  '/api/slots?floor=2',   'Slots on floor 2 only',              'SELECT ... WHERE floor = 2'),
    ('POST', '/api/slots',           'Add a new slot',                     'INSERT INTO parking_slots'),
    ('GET',  '/api/bookings',        'All bookings (admin view)',           '4-table LEFT JOIN query'),
    ('GET',  '/api/bookings?user_id=1','Bookings for one user',            'JOIN ... WHERE user_id = 1'),
    ('POST', '/api/bookings',        'Create a booking',                   'INSERT + UPDATE slot status'),
    ('POST', '/api/bookings/exit',   'Process exit + payment',             'Transaction: 3 UPDATEs'),
    ('GET',  '/api/users',           'All users (admin)',                   'SELECT id,name,email,phone FROM users'),
    ('POST', '/api/users/login',     'Authenticate user',                  'SELECT ... WHERE email=? AND password=?'),
    ('POST', '/api/users/register',  'Create new account',                 'INSERT INTO users'),
]

t = doc.add_table(rows=1 + len(api_rows), cols=4)
t.style     = 'Table Grid'
t.alignment = WD_TABLE_ALIGNMENT.LEFT
for i, h in enumerate(api_headers):
    cell = t.rows[0].cells[i]
    shade_cell(cell, NAVY)
    p = cell.paragraphs[0]; p.clear()
    r = p.add_run(h); r.bold = True; r.font.size = Pt(9.5); r.font.color.rgb = WHITE

method_colors = {'GET': RGBColor(0x0f,0x6e,0x56), 'POST': RGBColor(0x2b,0x6c,0xb0)}
for ri, (method, url, what, sql) in enumerate(api_rows):
    row  = t.rows[ri+1]
    bg   = RGBColor(0xf7,0xfa,0xfc) if ri % 2 == 0 else WHITE
    for c in row.cells: shade_cell(c, bg)

    p0 = row.cells[0].paragraphs[0]; p0.clear()
    r0 = p0.add_run(method); r0.bold = True; r0.font.size = Pt(9); r0.font.color.rgb = method_colors.get(method, NAVY)

    p1 = row.cells[1].paragraphs[0]; p1.clear()
    r1 = p1.add_run(url); r1.font.name = 'Courier New'; r1.font.size = Pt(8.5); r1.font.color.rgb = BLUE

    p2 = row.cells[2].paragraphs[0]; p2.clear()
    r2 = p2.add_run(what); r2.font.size = Pt(9); r2.font.color.rgb = NAVY

    p3 = row.cells[3].paragraphs[0]; p3.clear()
    r3 = p3.add_run(sql); r3.font.name = 'Courier New'; r3.font.size = Pt(8); r3.font.color.rgb = RGBColor(0x4a,0x55,0x68)

section_divider()

# ═══════════════════════════════════════════════════════════════════════════
#  SECTION 7 — PRESENTATION SCRIPT
# ═══════════════════════════════════════════════════════════════════════════
add_heading('7.  What to Say to Your Teacher — Presentation Script', 1)

add_note_box(
    'Tip: Open http://localhost:8080 and MySQL Workbench side-by-side. '
    'Run each SQL command, then refresh the browser tab. Let the teacher see the data change live.'
)

speeches = [
    ('Opening (30 seconds)',
     'Sir, this is ParkSmart — a Parking Space Management System built as a proper 3-tier application. '
     'The frontend is HTML, CSS, and JavaScript. The backend is Java using the built-in HTTP server. '
     'The database is MySQL. The browser talks to the Java server over HTTP, and the Java server talks '
     'to MySQL using JDBC. Nothing is hardcoded — all data comes from the database in real time.'),

    ('Explaining JDBC (1 minute)',
     'Sir, the JDBC connection is in DBConnection.java. I first load the MySQL driver using '
     'Class.forName("com.mysql.cj.jdbc.Driver") — this registers the driver with the JVM. '
     'Then for every query I call DriverManager.getConnection with the URL, username, and password. '
     'This opens a TCP connection to MySQL on port 3306 and returns a Connection object. '
     'I use PreparedStatement for all parameterised queries to prevent SQL injection. '
     'Results come back as a ResultSet which I iterate row by row using rs.next().'),

    ('Explaining the Transaction (30 seconds)',
     'Sir, when a vehicle exits, I use a JDBC transaction. I call setAutoCommit(false), '
     'then run three UPDATE statements — one on bookings, one on parking_slots, one on payments. '
     'Only if all three succeed do I call commit(). If any one fails, I call rollback() '
     'so the data stays consistent. This demonstrates the ACID property — specifically Atomicity.'),

    ('Live DML Demo (1 minute)',
     'Sir, I will now show that when I change data directly in MySQL Workbench and refresh the browser, '
     'the UI reflects it immediately — because every page load triggers a real JDBC query to MySQL. '
     'I will run: UPDATE parking_slots SET status = \'Available\' WHERE id = 3; '
     'Watch the Home page — slot S3 will turn green and the Available count will increase.'),

    ('Explaining the Schema (30 seconds)',
     'Sir, the schema has four tables — users, parking_slots, bookings, and payments. '
     'I used ENUM to restrict status and type columns so MySQL enforces valid values at the DB level. '
     'Foreign keys link bookings to both users and parking_slots with ON DELETE SET NULL. '
     'The Admin page uses a 4-table LEFT JOIN to show all booking details in a single query.'),

    ('Closing',
     'Sir, the code is fully separated into layers — the database layer is in the DAO classes, '
     'business logic is in the API handler, and the UI is in the frontend folder. '
     'Any table can be modified directly in MySQL and the change shows in the application '
     'without touching any code. Thank you sir.'),
]

for title, speech in speeches:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    r = p.add_run(title)
    r.bold = True; r.font.size = Pt(11); r.font.color.rgb = NAVY
    add_speak_box(speech)

# ── Save ────────────────────────────────────────────────────────────────────
output_path = r'C:\Users\BTech\OneDrive\Desktop\ER_Project\Files\UI\ParkSmart\ParkSmart_Project_Document.docx'
doc.save(output_path)
print(f'Saved: {output_path}')
