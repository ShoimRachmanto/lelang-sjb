# lelang-sjb
tampilan lelang ala SJB

ini teknik pushnya biasa aja
1. task scheduler akan menjalankan push_lelang_jumat.bat
push_lelang_jum'at.bat itu isinya akan menjalankan export_lelang_pekan_ini_new.py
isi export_lelang_pekan_ini_new.py lah yang mengenali kapan push_lelang_jumat.bat
kapan dieksekusinya, karena menentukan lelang pekan mana yang akan dipush
- kalau jumat siang, sabtu dan minggu, maka tentunya lelang pekan depan
- tapi kalau senin, maka biasanya sabtu dan minggu gagal, lalu manual di hari senin s.d. jumat pagi