docker-compose down
docker-compose up
docker-compose up -d
docker-compose up --build   ---- Kod Değiştirdiğinde (Önemli!)
# Sadece Worker loglarını izle
docker-compose logs -f worker

# Sadece Backend loglarını izle
docker-compose logs -f backend
docker-compose down -v ---- Veritabanı dahil her şeyi siler