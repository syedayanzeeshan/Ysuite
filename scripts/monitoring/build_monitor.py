#!/usr/bin/env python3
"""
Kernel Build Monitor for Radxa Rock 5B+ Development
Monitors kernel compilation process and logs build errors with criticality levels
"""

import os
import sys
import subprocess
import time
import signal
import multiprocessing
from datetime import datetime
from pathlib import Path
from loguru import logger
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.panel import Panel

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "scripts" / "analysis"))

from kernel_log_analyzer import KernelLogAnalyzer

console = Console()

class BuildMonitor:
    def __init__(self):
        self.analyzer = KernelLogAnalyzer()
        self.build_log = Path("../../logs/build/kernel_build.log")
        self.build_log.parent.mkdir(parents=True, exist_ok=True)
        
        # Configure build-specific logging
        logger.add(
            self.build_log,
            rotation="50 MB",
            retention="7 days",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )
        
        self.build_stats = {
            "start_time": None,
            "end_time": None,
            "errors": 0,
            "warnings": 0,
            "critical_errors": 0,
            "build_success": False
        }

    def log_build_event(self, message, level="info", context=None):
        """Log build events with appropriate criticality"""
        self.analyzer.log_error(message, level, context)
        
        if level == "critical":
            self.build_stats["critical_errors"] += 1
        elif level == "error":
            self.build_stats["errors"] += 1
        elif level == "warning":
            self.build_stats["warnings"] += 1

    def monitor_build_process(self, build_command, working_dir=None):
        """Monitor a kernel build process and log all events"""
        self.build_stats["start_time"] = datetime.now()
        
        console.print(f"[bold blue]Starting kernel build monitoring...[/bold blue]")
        console.print(f"Build command: {' '.join(build_command)}")
        
        try:
            # Start the build process
            process = subprocess.Popen(
                build_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                cwd=working_dir
            )
            
            # Monitor output in real-time
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Building kernel...", total=None)
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    
                    if output:
                        line = output.strip()
                        progress.update(task, description=f"Building... {line[:50]}...")
                        
                        # Analyze the line for criticality
                        criticality, pattern = self.analyzer.analyze_log_line(line)
                        
                        # Log based on criticality
                        if criticality in ["critical", "error"]:
                            self.log_build_event(
                                f"Build error: {line}",
                                criticality,
                                {"command": build_command, "pattern": pattern}
                            )
                        elif criticality == "warning":
                            self.log_build_event(
                                f"Build warning: {line}",
                                "warning",
                                {"command": build_command, "pattern": pattern}
                            )
                        
                        # Log to build log file
                        logger.info(line)
            
            # Check process result
            return_code = process.poll()
            self.build_stats["end_time"] = datetime.now()
            
            if return_code == 0:
                self.build_stats["build_success"] = True
                self.log_build_event("Kernel build completed successfully", "info")
                console.print("[bold green]✓ Build completed successfully![/bold green]")
            else:
                self.log_build_event(f"Build failed with return code: {return_code}", "error")
                console.print(f"[bold red]✗ Build failed with return code: {return_code}[/bold red]")
                
        except KeyboardInterrupt:
            self.log_build_event("Build interrupted by user", "warning")
            console.print("[yellow]Build interrupted by user[/yellow]")
            if process:
                process.terminate()
        except Exception as e:
            self.log_build_event(f"Build monitor error: {str(e)}", "critical")
            console.print(f"[bold red]Build monitor error: {str(e)}[/bold red]")

    def generate_build_report(self):
        """Generate a comprehensive build report"""
        if not self.build_stats["start_time"]:
            console.print("[yellow]No build data available[/yellow]")
            return
        
        duration = self.build_stats["end_time"] - self.build_stats["start_time"] if self.build_stats["end_time"] else None
        
        report = f"""
        Build Duration: {duration}
        Build Success: {'✓' if self.build_stats['build_success'] else '✗'}
        Critical Errors: {self.build_stats['critical_errors']}
        Errors: {self.build_stats['errors']}
        Warnings: {self.build_stats['warnings']}
        """
        
        console.print(Panel(report, title="Build Report", border_style="blue"))
        
        # Save detailed report
        report_file = Path("../../logs/build/build_report.txt")
        with open(report_file, "w") as f:
            f.write(f"Build Report - {datetime.now()}\n")
            f.write("=" * 50 + "\n")
            f.write(f"Start Time: {self.build_stats['start_time']}\n")
            f.write(f"End Time: {self.build_stats['end_time']}\n")
            f.write(f"Duration: {duration}\n")
            f.write(f"Success: {self.build_stats['build_success']}\n")
            f.write(f"Critical Errors: {self.build_stats['critical_errors']}\n")
            f.write(f"Errors: {self.build_stats['errors']}\n")
            f.write(f"Warnings: {self.build_stats['warnings']}\n")

def main():
    monitor = BuildMonitor()
    
    # Example build command for Radxa Rock 5B+
    import multiprocessing
    build_command = [
        "make", f"-j{multiprocessing.cpu_count()}",
        "ARCH=arm64",
        "CROSS_COMPILE=aarch64-linux-gnu-",
        # "rockchip_linux_defconfig"
    ]
    
    # You can modify this command based on your needs
    console.print("[bold blue]Kernel Build Monitor for Radxa Rock 5B+[/bold blue]")
    console.print("This will monitor the kernel build process and log all events.")
    
    # Start monitoring
    monitor.monitor_build_process(build_command, working_dir="/home/radxa/kernel-logging-env/linux")
    
    # Generate report
    monitor.generate_build_report()

if __name__ == "__main__":
    main() 
