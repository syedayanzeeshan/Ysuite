#!/usr/bin/env python3
"""
Kernel Configuration Utility for Radxa Rock 5B+ Development
Manages kernel configuration and logs configuration changes with criticality levels
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path
from loguru import logger
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class KernelConfigManager:
    def __init__(self, kernel_dir="../../linux"):
        self.kernel_dir = Path(kernel_dir)
        self.config_dir = Path("../../configs")
        self.config_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logger.add(
            Path("../../logs/config.log"),
            rotation="10 MB",
            retention="30 days",
            level="DEBUG",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
        )

    def log_config_event(self, message, level="info", context=None):
        """Log configuration events with appropriate criticality"""
        timestamp = datetime.now().isoformat()
        log_data = {
            "timestamp": timestamp,
            "message": message,
            "level": level,
            "context": context or {}
        }
        
        # Log to appropriate file based on level
        log_file = Path("../../logs") / f"{level}.log"
        with open(log_file, "a") as f:
            f.write(f"{json.dumps(log_data)}\n")
        
        # Also log to main config log
        if level == "critical":
            logger.critical(f"{message} | Context: {context}")
        elif level == "error":
            logger.error(f"{message} | Context: {context}")
        elif level == "warning":
            logger.warning(f"{message} | Context: {context}")
        else:
            logger.info(f"{message} | Context: {context}")

    def check_kernel_directory(self):
        """Check if kernel directory exists and is valid"""
        if not self.kernel_dir.exists():
            self.log_config_event(f"Kernel directory not found: {self.kernel_dir}", "error")
            console.print(f"[red]Kernel directory not found: {self.kernel_dir}[/red]")
            return False
        
        if not (self.kernel_dir / "Makefile").exists():
            self.log_config_event(f"Invalid kernel directory - no Makefile found: {self.kernel_dir}", "error")
            console.print(f"[red]Invalid kernel directory - no Makefile found: {self.kernel_dir}[/red]")
            return False
        
        self.log_config_event(f"Kernel directory validated: {self.kernel_dir}", "info")
        console.print(f"[green]✓ Kernel directory validated: {self.kernel_dir}[/green]")
        return True

    def backup_config(self, config_name="current"):
        """Backup current kernel configuration"""
        config_file = self.kernel_dir / ".config"
        backup_file = self.config_dir / f"{config_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.config"
        
        if not config_file.exists():
            self.log_config_event("No .config file found to backup", "warning")
            console.print("[yellow]No .config file found to backup[/yellow]")
            return None
        
        try:
            import shutil
            shutil.copy2(config_file, backup_file)
            self.log_config_event(f"Configuration backed up to: {backup_file}", "info")
            console.print(f"[green]✓ Configuration backed up to: {backup_file}[/green]")
            return backup_file
        except Exception as e:
            self.log_config_event(f"Failed to backup configuration: {str(e)}", "error")
            console.print(f"[red]Failed to backup configuration: {str(e)}[/red]")
            return None

    def load_defconfig(self, defconfig_name="rockchip_defconfig"):
        """Load a specific defconfig"""
        try:
            cmd = [
                "make", "ARCH=arm64", "CROSS_COMPILE=aarch64-linux-gnu-",
                f"{defconfig_name}"
            ]
            
            self.log_config_event(f"Loading defconfig: {defconfig_name}", "info")
            console.print(f"[blue]Loading defconfig: {defconfig_name}[/blue]")
            
            result = subprocess.run(
                cmd,
                cwd=self.kernel_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log_config_event(f"Successfully loaded defconfig: {defconfig_name}", "info")
                console.print(f"[green]✓ Successfully loaded defconfig: {defconfig_name}[/green]")
                return True
            else:
                self.log_config_event(f"Failed to load defconfig: {defconfig_name}", "error", 
                                   {"stderr": result.stderr})
                console.print(f"[red]Failed to load defconfig: {defconfig_name}[/red]")
                console.print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_config_event(f"Exception loading defconfig: {str(e)}", "critical")
            console.print(f"[red]Exception loading defconfig: {str(e)}[/red]")
            return False

    def menuconfig(self):
        """Open kernel configuration menu"""
        try:
            self.log_config_event("Opening kernel configuration menu", "info")
            console.print("[blue]Opening kernel configuration menu...[/blue]")
            
            cmd = [
                "make", "ARCH=arm64", "CROSS_COMPILE=aarch64-linux-gnu-",
                "menuconfig"
            ]
            
            result = subprocess.run(cmd, cwd=self.kernel_dir)
            
            if result.returncode == 0:
                self.log_config_event("Kernel configuration menu completed successfully", "info")
                console.print("[green]✓ Kernel configuration menu completed[/green]")
                return True
            else:
                self.log_config_event("Kernel configuration menu failed", "error")
                console.print("[red]Kernel configuration menu failed[/red]")
                return False
                
        except Exception as e:
            self.log_config_event(f"Exception in menuconfig: {str(e)}", "critical")
            console.print(f"[red]Exception in menuconfig: {str(e)}[/red]")
            return False

    def list_available_defconfigs(self):
        """List available defconfig files"""
        try:
            defconfig_dir = self.kernel_dir / "arch" / "arm64" / "configs"
            if not defconfig_dir.exists():
                self.log_config_event(f"Defconfig directory not found: {defconfig_dir}", "error")
                console.print(f"[red]Defconfig directory not found: {defconfig_dir}[/red]")
                return
            
            defconfigs = list(defconfig_dir.glob("*_defconfig"))
            
            if not defconfigs:
                self.log_config_event("No defconfig files found", "warning")
                console.print("[yellow]No defconfig files found[/yellow]")
                return
            
            table = Table(title="Available Defconfigs")
            table.add_column("Defconfig", style="cyan")
            table.add_column("Size", style="magenta")
            
            for defconfig in defconfigs:
                size = defconfig.stat().st_size
                table.add_row(defconfig.name, f"{size} bytes")
            
            console.print(table)
            self.log_config_event(f"Found {len(defconfigs)} defconfig files", "info")
            
        except Exception as e:
            self.log_config_event(f"Exception listing defconfigs: {str(e)}", "error")
            console.print(f"[red]Exception listing defconfigs: {str(e)}[/red]")

def main():
    config_manager = KernelConfigManager()
    
    console.print("[bold blue]Kernel Configuration Manager for Radxa Rock 5B+[/bold blue]")
    
    # Check kernel directory
    if not config_manager.check_kernel_directory():
        console.print("[red]Please ensure you're in the correct kernel directory[/red]")
        return
    
    # Show available options
    console.print("\n[bold]Available Operations:[/bold]")
    console.print("1. List available defconfigs")
    console.print("2. Load a defconfig")
    console.print("3. Open menuconfig")
    console.print("4. Backup current config")
    
    # For demonstration, let's list defconfigs
    config_manager.list_available_defconfigs()
    
    # Example: backup current config
    config_manager.backup_config("demo_backup")

if __name__ == "__main__":
    main() 