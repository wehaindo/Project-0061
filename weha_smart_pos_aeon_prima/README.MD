




10-03-2024
Changes

Problem 
1. Ketika payment method Prima QRIS sudah tergenerate QR-nya, system POS tidak boleh menghapus datanya. POS harus tetap menampilkan statusnya (init, approved, on-progress,decline,expired)

2.kalau ada kendala payment PRIMA QRIS (init, decline,expired), 
cashier bisa create payment method Prima QRIS baru, tanpa menghapus data payment method Prima QRIS sebelumnya (statusnya ditampilkan)

3.cashier bisa mencetak status payment PRIMA QRIS, berikut dengan detailnya, 
atas seluruh payment PRIMA QRIS yang terbentuk pada transaksi terkait.
cetakan status PRIMA QRIS, jika ada beberapa harus tercetak dalam satu kesatuan receipt

4.cetakan status PRIMA QRIS, bisa dicetak ulang. (bisa dipanggil lagi, bahkan ketika sudah beda hari)