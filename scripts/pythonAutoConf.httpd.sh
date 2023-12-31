#!/bin/bash
# location: /usr/local/sbin/

export OPENSSL_NO_DEFAULT_ZLIB=1
. /etc/rc.d/init.d/functions

if [ -f "/.jelenv" ]
then
    OLD_IFS=$IFS; IFS="$(printf '\n ')" && IFS="${IFS% }"
    vars="$(sed -r 's/([^=]+).*/\$\1/g' /.jelenv)"
    for env in $(cat /.jelenv); do
       env=$(echo "$env" | envsubst "$vars" )
       export "$env"
   done
   for env in $(cat /.jelenv); do
       env=$(echo "$env" | envsubst "$vars" )
       export "$env"
   done
   IFS=$OLD_IFS
fi

if [ -f /etc/sysconfig/httpd ]; then
    [ -z "$WSGI_SCRIPT" ] || {
        grep -qE "\s*WSGI_SCRIPT=$WSGI_SCRIPT" /etc/sysconfig/httpd || {
            sed -i '/\s*WSGI_SCRIPT/d' /etc/sysconfig/httpd
            echo "WSGI_SCRIPT=$WSGI_SCRIPT">>/etc/sysconfig/httpd
        }
    }
    . /etc/sysconfig/httpd
fi

[ -z "${WSGI_SCRIPT}" ] && export WSGI_SCRIPT="/var/www/webroot/ROOT/wsgi.py"

requirements_file="/var/www/webroot/ROOT/requirements.txt"
pip_log="/var/log/httpd/pip.log"

SED=$(which sed);
GREP=$(which grep);
RETVAL=0
STOP_TIMEOUT=${STOP_TIMEOUT-10}
RUN_DIR="/var/www/webroot/run";
DEFAULT_HTTPD_CONFIG="/etc/httpd/conf/httpd.conf";
let "MAX_CLIENTS_MEM=$(free -m|grep "Mem"|awk '{print $2}') / 30"
let "MAX_CLIENTS_CPU=$(grep -i "physical id" /proc/cpuinfo -c) * 5"
[ ${MAX_CLIENTS_MEM} -lt ${MAX_CLIENTS_CPU} ] && MAX_CLIENTS=${MAX_CLIENTS_MEM} || MAX_CLIENTS=${MAX_CLIENTS_CPU}

if [[ "$UID" == '0' ]]; then
    setcap 'cap_net_bind_service=+ep' $(realpath /usr/bin/python);
    chown -R apache:apache /var/log/httpd 2>&1
    [ -d /var/lib/dav/ ] || mkdir -p /var/lib/dav/;
    chown -R apache:apache /var/lib/dav/
    mkdir -p ${RUN_DIR}; chown -R apache:apache ${RUN_DIR};
    [ -d /var/www/icons/ ] && chown -R apache:apache /var/www/icons/
    [ -d /var/www/error/ ] && chown -R apache:apache /var/www/error/
    grep -qE '^export' /etc/sysconfig/httpd && sed -i 's/^export //' /etc/sysconfig/httpd
fi

backupConfig() {
    cp $1 $1.autobackup
}

fixSymlinks() {
    JELASTIC_PYTHON_BINARY_PATH=$(find /opt -name python 2>/dev/null|grep "jelastic-python[0-9]*/bin");
    [ -n "${JELASTIC_PYTHON_BINARY_PATH}" ] && JELASTIC_PYTHON_VERSION=$(${JELASTIC_PYTHON_BINARY_PATH} --version 2>&1|awk '{print $2}') || exit 0;
    CURRENT_PYTHON_VERSION=$(python -V 2>&1|awk '{print $2}');
    if [ "${CURRENT_PYTHON_VERSION}" != "${JELASTIC_PYTHON_VERSION}" ]; then
        version_index_short=$(awk -F "." '{ print $1$2}' <<< "$VERSION"); version_index=$(awk -F "." '{ print $1"."$2}' <<< "$VERSION"); major_version=$(awk -F "." '{ print $1}' <<< "$VERSION"); version=$VERSION; \
        [ -f /opt/jelastic-python${version_index_short}/bin/pip3 ] && ln -sfT /opt/jelastic-python${version_index_short}/bin/pip3 /opt/jelastic-python${version_index_short}/bin/pip; \
        ln -sfT /opt/jelastic-python${version_index_short}/bin/python /usr/bin/python; \
        ln -sfT /opt/jelastic-python${version_index_short}/bin/python /usr/bin/python${major_version}; \
        ln -sfT /opt/jelastic-python${version_index_short}/bin/python /usr/bin/python${version_index}; \
        ln -sfT /opt/jelastic-python${version_index_short}/bin/easy_install* /usr/bin/easy_install; \
        ln -sfT /opt/jelastic-python${version_index_short}/bin/python-config /usr/bin/python-config; \
        ln -sfT /opt/jelastic-python${version_index_short}/bin/virtualenv /usr/bin/virtualenv; \
        ln -sfT /opt/jelastic-python${version_index_short}/bin/python${version_index}-config /opt/jelastic-python${version_index_short}/bin/python-config; \
        ln -sfT /opt/jelastic-python${version_index_short}/bin/python-config /usr/bin/python${version_index}-config; \
        ln -sfT /opt/jelastic-python${version_index_short}/bin/python-config /usr/bin/python${major_version}-config; \
    fi
}

applyOptimization(){
    fixSymlinks
    [ -f ${requirements_file} ] && pip install -vvv --log ${pip_log} -r ${requirements_file} &>/dev/null;
    if $GREP -q -o -P "Jelastic autoconfiguration mark"  $DEFAULT_HTTPD_CONFIG
    then
        backupConfig $DEFAULT_HTTPD_CONFIG;
        $SED -i "/^\s*ServerLimit/c\ServerLimit     $MAX_CLIENTS" $DEFAULT_HTTPD_CONFIG;
        $SED -i "/prefork\.c/,/IfModule/ {s/^MaxRequestWorkers.*/MaxRequestWorkers $MAX_CLIENTS/}" $DEFAULT_HTTPD_CONFIG;
        $SED -i "/^\s*MaxConnectionsPerChild/c\MaxConnectionsPerChild     500" $DEFAULT_HTTPD_CONFIG;
        /usr/bin/setfacl -m g:ssh-access:wr  $DEFAULT_HTTPD_CONFIG >&/dev/null;
    fi
}
case "$1" in
    fixpermissions)
    if [[ "$UID" == '0' ]]; then
        chown -R apache:apache /var/log/httpd 2>&1
    fi
    ;;
    *)
    applyOptimization
    ;;
esac

