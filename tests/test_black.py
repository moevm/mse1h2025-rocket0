import subprocess
import sys

class CodeFormatterChecker:
    def __init__(self, target_directory: str = "./src"):
        self.target_directory = target_directory

    def execute_check(self) -> None:
        print("=== STARTING BLACK CODE FORMAT CHECK ===")

        try:
            process_result = subprocess.run(
                ["black", "--check", "--diff", "--color", self.target_directory],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            if process_result.returncode != 0:
                print("[WARNING] Formatting issues detected by Black.")
                print(process_result.stdout)
                print(process_result.stderr)
            else:
                print("[SUCCESS] All files are correctly formatted by Black.")

        except FileNotFoundError:
            print("[ERROR] Black is not installed or not found in the system PATH.")
            sys.exit(1)
        except Exception as error:
            print(f"[ERROR] An unexpected error occurred: {error}")
            sys.exit(1)

        print("=== BLACK CODE FORMAT CHECK COMPLETED ===\n")


if __name__ == "__main__":
    CodeFormatterChecker().execute_check()