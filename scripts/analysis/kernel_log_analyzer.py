#!/usr/bin/env python3
"""
Kernel Log Analyzer for Radxa Rock 5B+ Development
Analyzes kernel logs and categorizes errors by criticality level
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Configure logging
log_dir = Path("../../logs")
log_dir.mkdir(exist_ok=True)

logger.add(
    log_dir / "analysis.log",
    rotation="10 MB",
    retention="30 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)

console = Console()

class KernelLogAnalyzer:
    def __init__(self):
        self.critical_patterns = [
            r"Kernel panic",
            r"Unable to mount root",
            r"Fatal exception",
            r"System halted",
            r"Oops:",
            r"BUG:",
            r"Unable to handle kernel",
            r"Segmentation fault",
            r"Stack overflow",
            # Rockchip-specific critical patterns
            r"rockchip-pcie.*link.*failed",
            r"rockchip-cpufreq.*critical",
            r"rk3588.*thermal.*critical",
            r"coresight-mali.*fault",
            r"rockchip-efuse.*error",
            r"rk3588.*panic",
            r"rockchip.*fatal.*error"
        ]
        
        self.error_patterns = [
            r"ERROR:",
            r"Failed to",
            r"Could not",
            r"Unable to",
            r"Device not found",
            r"Module not found",
            r"Timeout",
            r"Connection refused",
            # Rockchip-specific error patterns
            r"rockchip-pinctrl.*error",
            r"rockchip-saradc.*failed",
            r"rockchip-otp.*error",
            r"pcie-rockchip.*error",
            r"rockchip-cpufreq.*failed",
            r"rockchip-efuse.*failed",
            r"rk3588.*error",
            r"rockchip.*driver.*failed"
        ]
        
        self.warning_patterns = [
            r"WARNING:",
            r"Warning:",
            r"Deprecated",
            r"Obsolete",
            r"Experimental",
            r"Unstable",
            # Rockchip-specific warning patterns
            r"rockchip.*warning",
            r"rk3588.*warning",
            r"rockchip-pcie.*warning",
            r"rockchip-cpufreq.*warning",
            r"coresight-mali.*warning"
        ]
        
        self.info_patterns = [
            r"INFO:",
            r"Info:",
            r"Loading",
            r"Initializing",
            r"Starting",
            r"Stopping"
        ]

    def analyze_log_line(self, line):
        """Analyze a single log line and return its criticality level"""
        line = line.strip()
        
        # Check critical patterns first
        for pattern in self.critical_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return "critical", pattern
                
        # Check error patterns
        for pattern in self.error_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return "error", pattern
                
        # Check warning patterns
        for pattern in self.warning_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return "warning", pattern
                
        # Check info patterns
        for pattern in self.info_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                return "info", pattern
                
        return "debug", None

    def log_error(self, message, criticality="info", context=None):
        """Log an error with appropriate criticality level"""
        timestamp = datetime.now().isoformat()
        
        log_data = {
            "timestamp": timestamp,
            "message": message,
            "criticality": criticality,
            "context": context or {}
        }
        
        # Log to appropriate file based on criticality
        log_file = log_dir / f"{criticality}.log"
        with open(log_file, "a") as f:
            f.write(f"{json.dumps(log_data)}\n")
        
        # Also log to main analysis log
        if criticality == "critical":
            logger.critical(f"{message} | Context: {context}")
        elif criticality == "error":
            logger.error(f"{message} | Context: {context}")
        elif criticality == "warning":
            logger.warning(f"{message} | Context: {context}")
        else:
            logger.info(f"{message} | Context: {context}")

    def analyze_log_file(self, log_file_path):
        """Analyze an entire log file"""
        if not os.path.exists(log_file_path):
            self.log_error(f"Log file not found: {log_file_path}", "error")
            return
            
        stats = {"critical": 0, "error": 0, "warning": 0, "info": 0, "debug": 0}
        
        with open(log_file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                criticality, pattern = self.analyze_log_line(line)
                stats[criticality] += 1
                
                if criticality in ["critical", "error"]:
                    self.log_error(
                        f"Line {line_num}: {line.strip()}",
                        criticality,
                        {"file": log_file_path, "line": line_num, "pattern": pattern}
                    )
        
        return stats

    def generate_report(self, stats):
        """Generate a rich formatted report"""
        table = Table(title="Kernel Log Analysis Report")
        table.add_column("Criticality Level", style="cyan")
        table.add_column("Count", style="magenta")
        table.add_column("Percentage", style="green")
        
        total = sum(stats.values())
        
        for level, count in stats.items():
            percentage = (count / total * 100) if total > 0 else 0
            table.add_row(level.upper(), str(count), f"{percentage:.1f}%")
        
        console.print(table)
        
        # Create summary panel
        critical_errors = stats.get("critical", 0) + stats.get("error", 0)
        summary = f"""
        Total Log Entries: {total}
        Critical/Error Entries: {critical_errors}
        Warning Entries: {stats.get('warning', 0)}
        Info Entries: {stats.get('info', 0)}
        """
        
        console.print(Panel(summary, title="Summary", border_style="blue"))

def main():
    analyzer = KernelLogAnalyzer()
    
    # Example usage
    console.print("[bold blue]Kernel Log Analyzer for Radxa Rock 5B+[/bold blue]")
    
    # Analyze a sample log file if it exists
    sample_log = "../../logs/build/kernel_build.log"
    if os.path.exists(sample_log):
        console.print(f"Analyzing log file: {sample_log}")
        stats = analyzer.analyze_log_file(sample_log)
        analyzer.generate_report(stats)
    else:
        console.print("[yellow]No log file found. Use this script to analyze kernel logs.[/yellow]")
        
        # Example of logging different types of errors
        analyzer.log_error("Kernel panic: unable to mount root filesystem", "critical", 
                         {"component": "filesystem", "board": "radxa-rock5b+"})
        analyzer.log_error("Module not found: xyz_driver", "error",
                         {"component": "driver", "module": "xyz_driver"})
        analyzer.log_error("Deprecated API used in driver", "warning",
                         {"component": "driver", "api": "deprecated_function"})

if __name__ == "__main__":
    main() 