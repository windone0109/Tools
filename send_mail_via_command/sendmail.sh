#!/bin/bash

#Created 2017-09-08
#VERSION 0.1 
#telnet smtp to send email with attachment
#USAGE:./sendemail.sh [attachment]



SMTPSERVER="172.16.100.151"
SMTPUSER="ntatest1@nta.com"
USER=`echo -n $SMTPUSER|base64`
PWD=`echo -n "111111"|base64`
RCPT="ntatest1@nta.com ntatest2@nta.com"

Recvlist=(${Recvlist[*]} $RCPT)
subjectName="email through telnet"
mailContext="edit your mail context"

function maild {
        (for a in "helo ntatest" "AUTH LOGIN" "$USER" "$PWD" "mail FROM:<$SMTPUSER>"; do
        sleep 1
        echo $a
        #sleep 1
done
for b in ${Recvlist[*]}
do
        echo "rcpt TO:<$b>"
        sleep 1
done
echo "data"
sleep 1
echo "from:<$SMTPUSER>"
echo "to:${Recvlist[*]}"
echo "subject:$subjectName"
echo  "Content-type: multipart/mixed; boundary=\"#BOUNDARY#\""
echo ""
echo "--#BOUNDARY#"
echo "Content-Type: text/plain; charset=UTF-8"
echo "Content-Transfer-Encoding: quoted-printable"
echo ""
echo "$mailContext"
echo "--#BOUNDARY#"
echo "Content-Type: application/octet-stream;name=\"$filename\""
echo "Content-Transfer-Encoding: base64"

echo ""
echo "$fileContent"
echo "--#BOUNDARY#--"
echo "."
sleep 1
echo "QUIT")|telnet $SMTPSERVER 25
}




if [ $# -gt 1 ]
then
echo "Usage:$0 [attachment]"
exit
fi


if [ $# -eq 0 ]
then
echo "send email with script as attachment"
filename=`basename $0`
fileContent=`cat $0|base64`
maild
else
filename=`basename $1`
if [ ! -e $filename ]
then
        echo "$filename not  exists"
        exit
else
        fileContent=`cat $1 |base64`
        #echo $fileContent
        maild
fi
fi
