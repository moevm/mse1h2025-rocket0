import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict

class PylintAnalyzer:
    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.issues = self._init_issues_dict()

    def _init_issues_dict(self) -> Dict[str, List[str]]:
        return {
            "C0111": [],
            "W0611": [],
            "W0612": [],
            "E1101": [],
            "R0903": [],
            "C0103": [],
            "R0914": [],
            "E0401": [],
            "E1120": [],
            "W0613": [],
        }

    def _collect_python_files(self) -> List[Path]:
        py_files = []
        for root, _, files in os.walk(self.directory):
            for f in files:
                if f.endswith(".py"):
                    py_files.append(Path(root) / f)
        return py_files

    def _execute_pylint(self, filepath: Path) -> str:
        try:
            completed = subprocess.run(
                ["pylint", "--output-format=text", str(filepath)],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.stderr:
                print(f"Ошибка pylint при анализе {filepath}:\n{completed.stderr}")
            return completed.stdout
        except Exception as ex:
            print(f"Не удалось запустить pylint для {filepath}: {ex}")
            return ""

    def _extract_issues(self, pylint_output: str) -> Dict[str, List[str]]:
        current_file_issues = {k: [] for k in self.issues.keys()}
        pattern = re.compile(r".*?:\d+:\d+: ([A-Z]\d+): (.+)")

        for line in pylint_output.splitlines():
            match = pattern.match(line)
            if match:
                code, message = match.groups()
                if code in self.issues:
                    self.issues[code].append(message)
                    current_file_issues[code].append(message)

        return current_file_issues

    def _log_file_report(self, filepath: Path, issues_by_code: Dict[str, List[str]]):
        print(f"Отчет по файлу: {filepath}")

        total_in_file = sum(len(msgs) for msgs in issues_by_code.values())

        if total_in_file == 0:
            print("Нарушений не обнаружено.")
            return

        for code, messages in issues_by_code.items():
            if not messages:
                continue

            severity = "Ошибка" if code.startswith("E") else "Предупреждение/Инфо"
            print(f"Код {code} - количество нарушений: {len(messages)}")
            
            for msg in messages:
                print(f"  * {msg}")

    def analyze(self):
        py_files = self._collect_python_files()

        if not py_files:
            print(f"В директории '{self.directory}' не найдено Python файлов.")
            return

        print("=" * 80)
        print("Запуск статического анализа с помощью pylint")

        for file_path in py_files:
            output = self._execute_pylint(file_path)

            if not output.strip():
                continue

            file_issues = self._extract_issues(output)

            self._log_file_report(file_path, file_issues)

        total_violations = sum(len(msgs) for msgs in self.issues.values())

        print("=" * 80)
        print("Общая статистика по всем проверенным файлам:")

        if total_violations == 0:
            print("Нарушений не обнаружено.")
        else:
            for code, messages in sorted(self.issues.items()):
                if messages:
                    count = len(messages)
                    severity = "Ошибка" if code.startswith("E") else "Предупреждение/Инфо"
                    print(f"{code} ({severity}): {count} нарушений")

        print("=" * 80)


if __name__ == "__main__":
    analyzer = PylintAnalyzer("src")
    analyzer.analyze()