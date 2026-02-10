# Python 3.10 kullanıyoruz (Full image, derleme sorunlarını önler)
FROM python:3.10

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıklarını kur (Full image olsa da bazı spesifik libler gerekebilir)
RUN apt-get update && apt-get install -y \
    libgomp1 \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    && rm -rf /var/lib/apt/lists/*

# Pip güncelle
RUN pip install --upgrade pip

# Kütüphaneleri kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kodları kopyala
COPY . .