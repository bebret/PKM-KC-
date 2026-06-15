# PKM-KC – Smart Cane IoT untuk Tunanetra

## Deskripsi Singkat
Proyek ini mengembangkan **tongkat pintar berbasis IoT** untuk membantu penyandang tunanetra dalam mendeteksi rintangan dan meningkatkan keselamatan mobilitas, khususnya saat berjalan di lingkungan ramai dan menyeberang jalan. Sistem menggunakan **sensor ultrasonik**, **sensor inframerah (IR)**, dan **ESP32** dengan **adaptive threshold** serta **sensor fusion** untuk meminimalkan noise dan false alarm.

---

## Latar Belakang
Tongkat konvensional hanya mendeteksi rintangan setelah terjadi kontak fisik. Di lingkungan perkotaan Indonesia (trotoar tidak rata, kendaraan parkir sembarangan), pendekatan ini berisiko. Oleh karena itu, diperlukan solusi preventif yang:
- Memberi peringatan **sebelum** terjadi tabrakan
- Tetap **ergonomis** dan mudah digunakan
- **Terjangkau** dan dapat diproduksi lokal

---

## Tujuan
- Mendeteksi rintangan jarak dekat dan menengah secara real-time
- Mengurangi noise sensor dengan **filtering** dan **adaptive threshold**
- Memberikan umpan balik intuitif (getaran & suara)
- Menyediakan fondasi pengembangan IoT (monitoring/telemetri)

---

## Fitur Utama
- **Sensor Fusion**: Ultrasonik + IR
- **Adaptive Threshold**: Ambang jarak dinamis sesuai kondisi
- **Anti-Noise**: Median/sliding window filter
- **Haptic Feedback**: Getaran bertingkat (PWM)
- **Audio Alert**: Buzzer (opsional)
- **IoT-Ready**: Wi-Fi ESP32 (opsional)

---

## Komponen Hardware
- ESP32 Dev Board
- Sensor Ultrasonik (HC-SR04)
- Sensor Infrared Obstacle
- Motor Getar (via transistor)
- Buzzer (opsional)
- Baterai Li-ion + modul charger
- Tongkat aluminium (housing prototipe)

---

## Software & Teknologi
- **Bahasa**: MicroPython
- **IDE**: Thonny / uPyCraft
- **Algoritma**:
  - Sliding window + median filter
  - Adaptive threshold berbasis perubahan jarak
  - Rule-based sensor fusion
- **IoT (opsional)**: HTTP/MQTT (ThingSpeak/Firebase)

---

## Struktur Repository
PKM-KC/
├─ main.py # Program utama ESP32 (MicroPython)
├─ config.py # Konfigurasi pin & parameter
├─ README.md # Dokumentasi proyek


## Cara Menjalankan
1. Flash firmware **MicroPython** ke ESP32
2. Upload `config.py` dan `main.py`
3. Sambungkan rangkaian sesuai pin
4. Nyalakan perangkat (powerbank/baterai)
5. Uji dengan objek di berbagai jarak

---

## Keunggulan
- Desain **realistis & ergonomis**
- **Low-cost**, komponen mudah didapat
- Modular & mudah dikembangkan
- Relevan dengan kondisi lokal Indonesia

---

## Pengembangan Lanjutan
- Navigasi berbasis graf (indoor)
- Deteksi zebra cross / traffic light
- AI ringan (klasifikasi rintangan)
- Aplikasi pendamping (Android)

---

## Lisensi
Proyek ini dikembangkan untuk keperluan akademik dan penelitian.


## Team Members
- Vincent Hon