
import csv

def csv_to_nested_dict(csv_file):
    data = {
        "S1": {},
        "S2": {}
    }

    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")

        for row in reader:
            semester = row["semestre"]
            unite = row["unite"]

            module = {
                "module_name": row["module_name"],
                "module_title": row["module_title"],
                "coef": int(row["coef"]),
                "credit": int(row["credit"]),
                "percent_tp": float(row["percent_tp"]),
                "percent_td": float(row["percent_td"]),
                "percent_exam": float(row["percent_exam"])
            }

            if unite not in data[semester]:
                data[semester][unite] = []

            data[semester][unite].append(module)

    return data


def modules_to_html(data):
    html = [
        '<html>',
        '<head><meta charset="utf-8"><title>Modules M1 GSI</title></head>',
        '<body>'
    ]

    for semester, unites in data.items():
        html.append(f"<h2>Semester {semester}</h2>")

        for unite, modules in unites.items():
            html.append(f"<h3>{unite}</h3>")
            html.append("<table border='1'>")

            html.append(
                "<tr>"
                "<th>Module Code</th>"
                "<th>Title</th>"
                "<th>Coef</th>"
                "<th>Credit</th>"
                "<th>TP%</th>"
                "<th>TD%</th>"
                "<th>Exam%</th>"
                "</tr>"
            )

            for info in modules:
                html.append("<tr>")
                html.append(f"<td>{info['module_name']}</td>")
                html.append(f"<td>{info['module_title']}</td>")
                html.append(f"<td>{info['coef']}</td>")
                html.append(f"<td>{info['credit']}</td>")
                html.append(f"<td>{info['percent_tp']:.0f}%</td>")
                html.append(f"<td>{info['percent_td']:.0f}%</td>")
                html.append(f"<td>{info['percent_exam']:.0f}%</td>")
                html.append("</tr>")

            html.append("</table><br>")

        html.append("<hr>")

    html.append("</body></html>")

    return "\n".join(html)


# Main program
if __name__ == "__main__":
    filename = "modules.csv"

    result = csv_to_nested_dict(filename)

    html_content = modules_to_html(result)

    with open("modules.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("HTML file generated: modules.html")
