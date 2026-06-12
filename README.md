# Şifreli P2P Haberleşme Sistemi

## Proje Amacı

Bu proje, TCP/IP protokolü kullanılarak ağ ortamında çalışan ve mesajları şifreleyerek ileten bir P2P (Peer-to-Peer) haberleşme sistemidir.

Sistem;

* Kullanıcı doğrulama
* Şifreli mesajlaşma
* Mesaj geçmişi kaydetme
* Sohbet dışa aktarma
* Tailscale ile farklı ağlarda haberleşme

özelliklerine sahiptir.

---

# Kullanılan Teknolojiler

* Python 3
* Socket Programming
* TCP/IP
* Threading
* SQLite3
* SHA-256
* Playfair Cipher (6x6 Türkçe Matris)
* Tailscale

---

# Proje Mimarisi

Sistem P2P mantığında çalışmaktadır.

```text
Kullanıcı A  ←────TCP/IP────→  Kullanıcı B
```

Merkezi mesaj sunucusu bulunmamaktadır.

Mesaj aktarımı için iki kullanıcının da çevrimiçi olması gerekmektedir.

---

# Klasör Yapısı

```text
SifreliHaberlesme/
│
├── network/
│   ├── __init__.py
│   ├── server.py
│   ├── client.py
│   └── peer.py
│
├── crypto/
│   ├── __init__.py
│   └── playfair.py
│
├── database/
│   ├── __init__.py
│   └── db.py
│
├── main.py
└── README.md
```

---

# Tamamlanan Özellikler

## 1. TCP/IP Haberleşme

Socket programlama kullanılarak cihazlar arasında doğrudan bağlantı kurulmaktadır.

Özellikler:

* TCP tabanlı haberleşme
* Çoklu cihaz desteği
* Tailscale üzerinden bağlantı

---

## 2. Threading

Aynı anda:

* Mesaj gönderme
* Mesaj alma

işlemleri gerçekleştirilebilmektedir.

---

## 3. Playfair Şifreleme

Türkçe karakterleri destekleyen özel 6x6 matris kullanılmaktadır.

Örnek karakter seti:

```text
a b c ç d e
f g ğ h ı i
j k l m n o
ö p r s ş t
u ü v y z
. , ! ? : &
```

Özellikler:

* Türkçe karakter desteği
* Boşluk desteği
* Noktalama desteği
* Kullanıcı tarafından belirlenen anahtar desteği

---

## 4. Kullanıcı Sistemi

Kullanıcılar:

* Kayıt olabilir
* Giriş yapabilir

Bilgiler SQLite veritabanında saklanmaktadır.

---

## 5. SHA-256 Parola Güvenliği

Parolalar düz metin olarak tutulmaz.

Örnek:

```text
1234
```

şu şekilde saklanır:

```text
03ac674216f3e15c761ee1a5e255f067...
```

---

## 6. Sohbet Geçmişi

Mesajlar SQLite üzerinde saklanmaktadır.

Tutulan bilgiler:

* Gönderen kullanıcı
* Mesaj içeriği
* Tarih
* Saat

---

## 7. Mesaj Silme

Komut:

```text
/sil
```

Mesajlar ID numarası ile silinebilir.

---

## 8. Sohbet Geçmişini Görüntüleme

Komut:

```text
/gecmis
```

Geçmiş sohbet kayıtları görüntülenebilir.

---

## 9. Sohbeti Dışa Aktarma

Komut:

```text
/export
```

Sohbet geçmişi:

```text
chat_export.txt
```

dosyasına aktarılır.

---

## 10. Tailscale Desteği

Sistem yalnızca aynı Wi-Fi ağı üzerinde değil, farklı internet ağları üzerinden de çalışabilmektedir.

Örnek:

```text
Edirne ←────→ İstanbul
```

Bağlantı için Tailscale ağı kullanılmaktadır.

---

# Kullanım

Program başlatılır:

```bash
python3 -m network.peer
```

Windows:

```cmd
py -m network.peer
```

---

# Giriş İşlemi

```text
1 - Kayıt Ol
2 - Giriş Yap
```

---

# Şifreleme Anahtarı

Her kullanıcı aynı oturum anahtarını girmelidir.

Örnek:

```text
Şifreleme Anahtarı:
trakya2025
```

Anahtarlar farklı olursa mesajlar doğru çözülemez.

---

# Bağlantı Modları

## 1. Bağlantı Bekle

```text
1 - Bağlantı Bekle
```

Kullanıcı bağlantı bekleyen taraf olur.

---

## 2. Bir Cihaza Bağlan

```text
2 - Bir Cihaza Bağlan
```

Karşı cihazın Tailscale IP adresi girilir.

Örnek:

```text
100.124.216.57
```

---

# Bilinen Kısıtlar

Sistem P2P mimaride çalıştığı için:

* İki kullanıcının da çevrimiçi olması gerekir.
* Çevrimdışı kullanıcıya mesaj bırakılamaz.
* Mesajlar merkezi sunucuda tutulmaz.

Bu durum bilinçli olarak tercih edilmiştir.

---

# Gelecek Çalışmalar

## GUI

CustomTkinter kullanılarak:

* Giriş ekranı
* Kayıt ekranı
* Sohbet ekranı

geliştirilecektir.

---

## Dosya Transferi

Şifreli dosya gönderimi eklenebilir.

---

## Otomatik Anahtar Yönetimi

Şu an kullanıcılar anahtarı manuel girmektedir.

İlerleyen sürümlerde:

* Oturum anahtarı üretimi
* Anahtar değişimi

eklenmesi planlanmaktadır.

---

# Proje Durumu

Mevcut sürüm:

✅ P2P Haberleşme

✅ TCP/IP

✅ Tailscale Desteği

✅ Şifreli Mesajlaşma

✅ Kullanıcı Yönetimi

✅ SQLite Veritabanı

✅ Sohbet Geçmişi

✅ Mesaj Silme

✅ Sohbet Dışa Aktarma

Proje GUI geliştirme aşamasına geçmeye hazırdır.
