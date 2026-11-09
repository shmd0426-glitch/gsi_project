
import csv
import json

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


# Main program
if __name__ == "__main__":
    filename = "modules.csv"

    result = csv_to_nested_dict(filename)

    print(json.dumps(result, indent=4, ensure_ascii=False))
