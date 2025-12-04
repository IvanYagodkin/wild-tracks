#!/data/data/com.termux/files/usr/bin/bash

echo "Проверка: все ли фото есть в metadata/observations.csv?"

for img in images/*; do
  filename=$(basename "$img")
  if grep -q "$filename" metadata/observations.csv; then
    echo "✅ $filename — есть в базе"
  else
    echo "❌ $filename — НЕТ в базе!"
  fi
done
