from flask import Flask, render_template_string, url_for

app = Flask(__name__)


HOME_PAGE = """
<!doctype html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>Home</title>
	<style>
		body { font-family: Arial, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }
		.wrap { max-width: 900px; margin: 0 auto; padding: 48px 20px; }
		.card { background: #111827; border: 1px solid #334155; border-radius: 16px; padding: 28px; }
		a { color: #60a5fa; text-decoration: none; }
	</style>
</head>
<body>
	<div class="wrap">
		<div class="card">
			<h1>First Flask Page</h1>
			<p>This is the existing page.</p>
			<p><a href="{{ url_for('second_page') }}">Open the second page</a></p>
		</div>
	</div>
</body>
</html>
"""


SECOND_PAGE = """
<!doctype html>
<html lang="en">
<head>
	<meta charset="utf-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
	<title>Second Page</title>
	<style>
		:root { color-scheme: dark; }
		body {
			margin: 0;
			min-height: 100vh;
			font-family: Arial, sans-serif;
			display: grid;
			place-items: center;
			background: linear-gradient(135deg, #111827, #1d4ed8);
			color: #f8fafc;
		}
		.panel {
			width: min(900px, calc(100% - 32px));
			background: rgba(15, 23, 42, 0.9);
			border: 1px solid rgba(148, 163, 184, 0.2);
			border-radius: 20px;
			padding: 36px;
			box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
		}
		.grid {
			display: grid;
			gap: 16px;
			grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		}
		.tile {
			background: rgba(30, 41, 59, 0.9);
			border: 1px solid rgba(148, 163, 184, 0.15);
			border-radius: 16px;
			padding: 18px;
		}
		.btn {
			display: inline-block;
			margin-top: 22px;
			padding: 12px 18px;
			border-radius: 999px;
			background: #38bdf8;
			color: #082f49;
			font-weight: 700;
			text-decoration: none;
		}
	</style>
</head>
<body>
	<main class="panel">
		<h1>Second Flask Webapp Page</h1>
		<p>This is a separate page for your second Flask route.</p>

		<div class="grid">
			<div class="tile">
				<h3>Feature One</h3>
				<p>Put new content here.</p>
			</div>
			<div class="tile">
				<h3>Feature Two</h3>
				<p>Use this area for a different workflow.</p>
			</div>
			<div class="tile">
				<h3>Feature Three</h3>
				<p>Add charts, forms, or controls here.</p>
			</div>
		</div>

		<a class="btn" href="{{ url_for('home') }}">Back to first page</a>
	</main>
</body>
</html>
"""


@app.route("/")
def home():
	return render_template_string(HOME_PAGE)


@app.route("/page2")
def second_page():
	return render_template_string(SECOND_PAGE)


if __name__ == "__main__":
	app.run(debug=True)
