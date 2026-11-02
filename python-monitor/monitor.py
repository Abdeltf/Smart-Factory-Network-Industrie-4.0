
import subprocess
import csv
import os
import tkinter as tk
from tkinter import ttk
from datetime import datetime

devices = {
    "My Computer": "127.0.0.1",
    "Local Router": "192.168.1.1"
}

LOG_FILE = "monitoring_log.csv"
INTERVAL = 10000


class SmartFactoryMonitor:

    def __init__(self, root):
        self.root = root
        self.root.title("Smart Factory - Network Monitor")
        self.root.geometry("900x550")
        self.root.configure(bg="#eef2f5")

        self.running = True
        self.online_count = 0
        self.offline_count = 0
        self.after_id = None

        self.device_stats = {
            device: {"checks": 0, "online": 0}
            for device in devices
        }

        # Load previous monitoring results
        self.load_history()

        self.create_dashboard()
        self.check_devices()

    def load_history(self):

        if not os.path.exists(LOG_FILE):
            return

        try:
            with open(LOG_FILE, "r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    device = row.get("Device", "")
                    status = row.get("Status", "").strip().upper()

                    if device in self.device_stats:
                        if status in ("ONLINE", "OFFLINE"):
                            stats = self.device_stats[device]
                            stats["checks"] += 1

                            if status == "ONLINE":
                                stats["online"] += 1

            print("Previous monitoring history loaded.")

        except (OSError, csv.Error) as error:
            print(f"Could not load monitoring history: {error}")

    def create_dashboard(self):

        title = tk.Label(
            self.root,
            text="SMART FACTORY NETWORK MONITOR",
            font=("Arial", 20, "bold"),
            bg="#eef2f5",
            fg="#20354a"
        )
        title.pack(pady=(25, 5))

        subtitle = tk.Label(
            self.root,
            text="Network Monitoring | Industrie 4.0",
            font=("Arial", 11),
            bg="#eef2f5",
            fg="#607080"
        )
        subtitle.pack(pady=(0, 20))

        stats_frame = tk.Frame(self.root, bg="#eef2f5")
        stats_frame.pack(pady=10)

        self.online_label = tk.Label(
            stats_frame,
            text="ONLINE: 0",
            font=("Arial", 15, "bold"),
            fg="#168447",
            bg="#eef2f5",
            width=18
        )
        self.online_label.pack(side="left", padx=15)

        self.offline_label = tk.Label(
            stats_frame,
            text="OFFLINE: 0",
            font=("Arial", 15, "bold"),
            fg="#c0392b",
            bg="#eef2f5",
            width=18
        )
        self.offline_label.pack(side="left", padx=15)

        summary_frame = tk.Frame(self.root, bg="#eef2f5")
        summary_frame.pack(pady=8)

        self.total_checks_label = tk.Label(
            summary_frame,
            text="TOTAL CHECKS: 0",
            font=("Arial", 12, "bold"),
            fg="#20354a",
            bg="#eef2f5",
            width=22
        )
        self.total_checks_label.pack(side="left", padx=15)

        self.availability_label = tk.Label(
            summary_frame,
            text="OVERALL AVAILABILITY: 0%",
            font=("Arial", 12, "bold"),
            fg="#168447",
            bg="#eef2f5",
            width=28
        )
        self.availability_label.pack(side="left", padx=15)

        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=30, pady=20)

        columns = (
            "device", "ip", "status",
            "availability", "last_check"
        )

        self.table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=8
        )

        self.table.heading("device", text="Device")
        self.table.heading("ip", text="IP Address")
        self.table.heading("status", text="Status")
        self.table.heading("availability", text="Availability")
        self.table.heading("last_check", text="Last Check")

        self.table.column("device", width=190)
        self.table.column("ip", width=130)
        self.table.column("status", width=100)
        self.table.column("availability", width=110)
        self.table.column("last_check", width=170)

        self.table.tag_configure("online", foreground="green")
        self.table.tag_configure("offline", foreground="red")

        self.table.pack(fill="both", expand=True)

        button_frame = tk.Frame(self.root, bg="#eef2f5")
        button_frame.pack(pady=15)

        self.check_button = ttk.Button(
            button_frame,
            text="Check Now",
            command=self.check_now
        )
        self.check_button.pack(side="left", padx=10)
        history_button = ttk.Button(
    button_frame,
    text="View History",
    command=self.show_history
)
        history_button = ttk.Button(
            button_frame,
            text="View History",
            command=self.show_history
        )
        history_button.pack(side="left", padx=10)

        self.time_label = tk.Label(
            self.root,
            text="Starting monitoring...",
            font=("Arial", 9),
            bg="#eef2f5",
            fg="#607080"
        )
        self.time_label.pack(pady=(0, 15))


    def show_history(self):

        history_window = tk.Toplevel(self.root)
        history_window.title("Smart Factory - Monitoring History")
        history_window.geometry("850x450")
        history_window.configure(bg="#eef2f5")

        title = tk.Label(
            history_window,
            text="MONITORING HISTORY",
            font=("Arial", 18, "bold"),
            bg="#eef2f5",
            fg="#20354a"
        )
        title.pack(pady=15)

        description = tk.Label(
            history_window,
            text="Previous network connectivity checks",
            font=("Arial", 10),
            bg="#eef2f5",
            fg="#607080"
        )
        description.pack(pady=5)

        table_frame = tk.Frame(history_window)
        table_frame.pack(fill="both", expand=True, padx=20, pady=15)

        columns = ("timestamp", "device", "ip", "status", "availability")

        history_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        history_table.heading("timestamp", text="Timestamp")
        history_table.heading("device", text="Device")
        history_table.heading("ip", text="IP Address")
        history_table.heading("status", text="Status")
        history_table.heading("availability", text="Availability")

        history_table.column("timestamp", width=160)
        history_table.column("device", width=160)
        history_table.column("ip", width=120)
        history_table.column("status", width=100)
        history_table.column("availability", width=120)

        history_table.tag_configure("online", foreground="green")
        history_table.tag_configure("offline", foreground="red")

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=history_table.yview
        )

        history_table.configure(yscrollcommand=scrollbar.set)

        history_table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        try:
            with open(LOG_FILE, "r", newline="", encoding="utf-8") as file:

                reader = csv.DictReader(file)
                records = list(reader)

                # Display the latest 100 records
                for row in records[-100:]:

                    status = row.get("Status", "").upper()
                    tag = "online" if status == "ONLINE" else "offline"

                    history_table.insert(
                        "",
                        "end",
                        values=(
                            row.get("Timestamp", ""),
                            row.get("Device", ""),
                            row.get("IP", ""),
                            status,
                            row.get("Availability", "")
                        ),
                        tags=(tag,)
                    )

            record_count = tk.Label(
                history_window,
                text=f"Total records: {len(records)} | Showing latest 100 at most",
                font=("Arial", 9),
                bg="#eef2f5",
                fg="#607080"
            )
            record_count.pack(pady=10)

        except FileNotFoundError:
            tk.Label(
                history_window,
                text="No monitoring history available yet.",
                bg="#eef2f5"
            ).pack(pady=10)

        except (OSError, csv.Error) as error:
            tk.Label(
                history_window,
                text=f"Could not read history: {error}",
                bg="#eef2f5",
                fg="red"
            ).pack(pady=10)

    def ping_device(self, ip):

        try:
            result = subprocess.run(
                ["ping", "-n", "1", "-w", "1000", ip],
                capture_output=True,
                text=True,
                encoding="cp850",
                errors="replace",
                timeout=3
            )

            output = result.stdout.lower()

            reply_found = (
                f"reply from {ip}" in output
                or f"réponse de {ip}" in output
            )

            error_found = (
                "unreachable" in output
                or "inaccessible" in output
                or "injoignable" in output
            )

            return reply_found and not error_found

        except (subprocess.TimeoutExpired, OSError):
            return False

    def check_now(self):

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        self.check_devices()

    def check_devices(self):

        if not self.running:
            return

        self.after_id = None
        self.online_count = 0
        self.offline_count = 0

        for item in self.table.get_children():
            self.table.delete(item)

        with open(LOG_FILE, "a", newline="", encoding="utf-8") as file:

            writer = csv.writer(file)

            if os.path.getsize(LOG_FILE) == 0:
                writer.writerow([
                    "Timestamp", "Device", "IP",
                    "Status", "Availability"
                ])

            for device, ip in devices.items():

                online = self.ping_device(ip)
                stats = self.device_stats[device]

                stats["checks"] += 1

                if online:
                    status = "ONLINE"
                    tag = "online"
                    self.online_count += 1
                    stats["online"] += 1
                else:
                    status = "OFFLINE"
                    tag = "offline"
                    self.offline_count += 1

                availability = (
                    stats["online"] / stats["checks"]
                ) * 100

                timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                self.table.insert(
                    "",
                    "end",
                    values=(
                        device,
                        ip,
                        status,
                        f"{availability:.1f}%",
                        timestamp
                    ),
                    tags=(tag,)
                )

                writer.writerow([
                    timestamp,
                    device,
                    ip,
                    status,
                    f"{availability:.1f}%"
                ])

            file.flush()

            total_checks = sum(
            stats["checks"]
            for stats in self.device_stats.values()
        )

        successful_checks = sum(
            stats["online"]
            for stats in self.device_stats.values()
        )

        overall_availability = (
            successful_checks / total_checks * 100
            if total_checks > 0 else 0
        )
        self.online_label.config(
            text=f"ONLINE: {self.online_count}"
        )

        self.offline_label.config(
            text=f"OFFLINE: {self.offline_count}"
        )
        self.total_checks_label.config(
            text=f"TOTAL CHECKS: {total_checks}"
        )

        self.availability_label.config(
            text=f"OVERALL AVAILABILITY: {overall_availability:.1f}%"
        )

        self.time_label.config(
            text=f"Last update: {datetime.now().strftime('%H:%M:%S')} | Next check in 10 seconds"
        )

        if self.running:
            self.after_id = self.root.after(
                INTERVAL,
                self.check_devices
            )

    def close_application(self):

        self.running = False

        if self.after_id is not None:
            self.root.after_cancel(self.after_id)

        self.root.destroy()


if __name__ == "__main__":

    root = tk.Tk()
    app = SmartFactoryMonitor(root)
    root.mainloop()
