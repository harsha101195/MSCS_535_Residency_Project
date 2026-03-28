const express = require("express");
const app = express();
const port = 3000;

// Read form data
app.use(express.urlencoded({ extended: true }));

// Escape HTML so user input is displayed as text instead of running as code
function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// Add CSP only to safe routes
app.use((req, res, next) => {
  const safeRoutes = ["/xss-safe", "/eval-safe"];
  if (safeRoutes.includes(req.path)) {
    res.setHeader(
      "Content-Security-Policy",
      "default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none';"
    );
  }
  next();
});

// Home page
app.get("/", (req, res) => {
  res.send(`
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>JavaScript Security Demo</title>
        <style>
          body { font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; line-height: 1.6; }
          .card { border: 1px solid #ccc; padding: 20px; margin-bottom: 20px; border-radius: 8px; }
          a { text-decoration: none; color: blue; }
        </style>
      </head>
      <body>
        <h1>JavaScript Security Demo</h1>
        <p>This project shows unsafe and safe ways to handle JavaScript security problems.</p>

        <div class="card">
          <h2>XSS Demo</h2>
          <p><a href="/xss-unsafe">Go to Unsafe XSS Demo</a></p>
          <p><a href="/xss-safe">Go to Safe XSS Demo</a></p>
        </div>

        <div class="card">
          <h2>eval() Demo</h2>
          <p><a href="/eval-unsafe">Go to Unsafe eval() Demo</a></p>
          <p><a href="/eval-safe">Go to Safe eval() Demo</a></p>
        </div>
      </body>
    </html>
  `);
});

// Unsafe XSS page
app.get("/xss-unsafe", (req, res) => {
  const name = req.query.name || "";

  res.send(`
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Unsafe XSS Demo</title>
      </head>
      <body>
        <h1>Unsafe XSS Demo</h1>
        <p>This page puts user input directly into HTML.</p>

        <form method="GET" action="/xss-unsafe">
          <label>Enter text:</label><br />
          <input type="text" name="name" style="width: 400px;" />
          <button type="submit">Submit</button>
        </form>

        <h2>Output:</h2>
        <div>${name}</div>

        <p><a href="/">Back to Home</a></p>
      </body>
    </html>
  `);
});

// Safe XSS page
app.get("/xss-safe", (req, res) => {
  const name = req.query.name || "";
  const safeName = escapeHtml(name);

  res.send(`
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Safe XSS Demo</title>
      </head>
      <body>
        <h1>Safe XSS Demo</h1>
        <p>This page escapes user input before putting it into HTML.</p>
        <p>CSP is enabled on this page.</p>

        <form method="GET" action="/xss-safe">
          <label>Enter text:</label><br />
          <input type="text" name="name" style="width: 400px;" />
          <button type="submit">Submit</button>
        </form>

        <h2>Output:</h2>
        <div>${safeName}</div>

        <p><a href="/">Back to Home</a></p>
      </body>
    </html>
  `);
});

// Unsafe eval page
app.get("/eval-unsafe", (req, res) => {
  const expression = req.query.expression || "";
  let result = "";

  try {
    result = expression ? eval(expression) : "";
  } catch (err) {
    result = "Error: " + err.message;
  }

  res.send(`
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Unsafe eval Demo</title>
      </head>
      <body>
        <h1>Unsafe eval() Demo</h1>
        <p>This page uses <code>eval()</code> on user input.</p>

        <form method="GET" action="/eval-unsafe">
          <label>Enter expression:</label><br />
          <input type="text" name="expression" style="width: 400px;" placeholder="2+3" />
          <button type="submit">Run</button>
        </form>

        <h2>Result:</h2>
        <div>${escapeHtml(String(result))}</div>

        <p><a href="/">Back to Home</a></p>
      </body>
    </html>
  `);
});

// Safe eval page
app.get("/eval-safe", (req, res) => {
  const { op, a, b } = req.query;
  let result = "";

  const operations = {
    add: (x, y) => x + y,
    sub: (x, y) => x - y,
    mul: (x, y) => x * y,
    div: (x, y) => {
      if (y === 0) throw new Error("Division by zero");
      return x / y;
    }
  };

  if (op && a !== undefined && b !== undefined) {
    const x = Number(a);
    const y = Number(b);

    if (!Number.isFinite(x) || !Number.isFinite(y)) {
      result = "Invalid numeric input";
    } else if (!Object.prototype.hasOwnProperty.call(operations, op)) {
      result = "Unsupported operation";
    } else {
      try {
        result = operations[op](x, y);
      } catch (err) {
        result = "Error: " + err.message;
      }
    }
  }

  res.send(`
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>Safe eval Demo</title>
      </head>
      <body>
        <h1>Safe eval() Demo</h1>
        <p>This page does not use <code>eval()</code>. It only allows specific safe operations.</p>
        <p>CSP is enabled on this page.</p>

        <form method="GET" action="/eval-safe">
          <label>Operation:</label><br />
          <select name="op">
            <option value="add">add</option>
            <option value="sub">sub</option>
            <option value="mul">mul</option>
            <option value="div">div</option>
          </select>
          <br /><br />

          <label>a:</label><br />
          <input type="text" name="a" />
          <br /><br />

          <label>b:</label><br />
          <input type="text" name="b" />
          <br /><br />

          <button type="submit">Calculate</button>
        </form>

        <h2>Result:</h2>
        <div>${escapeHtml(String(result))}</div>

        <p><a href="/">Back to Home</a></p>
      </body>
    </html>
  `);
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});