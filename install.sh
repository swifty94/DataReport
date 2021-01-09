#!/bin/bash
lib=$(pip3 freeze|grep mysql-connector-python|wc -l)
if (( $lib < 1 )); then
    cd lib/
	pip install * -f ./ --no-index
    for i in $(ls *.whl -l|awk '{print $9}'); 
        do 
            echo "[$(date +'%Y-%m-%d %R:%S')][INFO][Module:OSSGINAL -> [OS:$(uname -s)][Node:$(uname -n)] -> Installed wheel > $i" >> ../cpe_report.log            
    done
    
fi