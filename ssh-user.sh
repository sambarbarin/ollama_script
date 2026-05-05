cat > /etc/motd <<EOF

__________________________________________________________________________

        ================== ** W A R N I N G ** ==================

    Authorized uses only. All activity may be monitored and reported.
    Disconnect IMMEDIATELY if you are not an authorized user !
__________________________________________________________________________


EOF

cat > /etc/issue <<EOF
############################  Authorized users only  ############################
#                                                                               #
# This computer system including all related equipment and network devices      #
# (specifically including Internet access) is provided only for authorized      #
# use and authorized users. Unauthorized users are prohibited.                  #
#                                                                               #
# Users (authorized or unauthorized) have no explicit or implicit expectation   #
# of privacy. Any or all uses of this system may be subject to one or more of   #
# the following actions: interception, monitoring, recording, auditing,         #
# inspection and disclosure to security personnel and law enforcement personnel,#
# as well as authorized officials of other agencies, both domestic and foreign. #
#                                                                               #
# By using this system, you consent to these actions. Unauthorized or improper  #
# use of this system may result in administrative disciplinary action and       #
# civil and criminal penalties. By accessing this system you indicate your      #
# awareness of and consent to these terms and conditions of use.                #
#                                                                               #
# Discontinue access immediately if you do not agree to the conditions stated   #
# in this notice.                                                               #
#                                                                               #
#################################################################################
EOF

cat /etc/issue > /etc/issue.net

cat > /etc/profile.d/login-info.sh <<EOF
#! /usr/bin/env bash

# Basic info
HOSTNAME=`uname -n`
OS_VERSION=`cat /etc/redhat-release | awk {'print $0'}`
IP1=`hostname -I | awk {'print $1'}`
IP2=`hostname -I | awk {'print $2'}`
BANNER=`cat /etc/motd`
NBPROC=`expr $(tail -n 30 /proc/cpuinfo | grep processor | awk '{print $3}') + 1`

# System load
MEMORY1=`free -t -m | grep Total | awk '{print $3" MB";}'`
MEMORY2=`free -t -m | grep "Mem" | awk '{print $2" MB";}'`
MEMORY3=`free | grep Mem | awk '{print $3/$2 * 100.0}'`
SWAP1=`free -m | tail -n 1 | awk '{print $3" MB"}'`
SWAP2=`free -m | tail -n 1 | awk '{print $2" MB"}'`
LOAD1=`cat /proc/loadavg | awk {'print $1'}`
LOAD5=`cat /proc/loadavg | awk {'print $2'}`
LOAD15=`cat /proc/loadavg | awk {'print $3'}`
CPU_PERCENTAGE=`mpstat | grep all | awk '{printf ($4+$5+$6)}'`

echo "
=====================================================================
 - Hostname ...........: $HOSTNAME
 - IP Prod ............: $IP1
 - IP Service .........: $IP2
 - Version OS .........: $OS_VERSION
=====================================================================
 - NB CPU .............: $NBPROC
 - CPU load average ...: $LOAD1, $LOAD5, $LOAD15 (1, 5, 15 min)
 - CPU used % .........: $CPU_PERCENTAGE %
=====================================================================
 - Memory used ........: $MEMORY1 / $MEMORY2
 - Memory used % ......: $MEMORY3 %
 - Swap used ..........: $SWAP1 / $SWAP2
=====================================================================
"
EOF

chmod 0644 /etc/profile.d/login-info.sh

