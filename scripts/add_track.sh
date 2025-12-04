#!/data/data/com.termux/files/usr/bin/bash

echo "Добавляем новый след"
echo -n "Вид животного: "
read animal
echo -n "Дата (ГГГГ-ММ-ДД): "
read date
echo -n "Время (ЧЧ:ММ): "
read time
echo -n "Место: "
read location
echo -n "Описание: "
read description
echo -n "Имя файла фото (в папке images/): "
read photo

echo "$photo,$animal,$date,$time,$location,,,$description" >> metadata/observations.csv
echo "✅ След добавлен в metadata/observations.csv"
