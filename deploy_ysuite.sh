echo "YSuite - Rock 5B+ Monitoring Suite"
echo "Deploying to board..."
scp ysuite.py radxa@192.168.10.16:/tmp/
scp install_ysuite.sh radxa@192.168.10.16:/tmp/
sshpass -p "radxa" ssh -o StrictHostKeyChecking=no radxa@192.168.10.16 "sudo bash /tmp/install_ysuite.sh"
