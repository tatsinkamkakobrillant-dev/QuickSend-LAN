from feature.transfer_service import TransferService

service = TransferService("receptions", port=50555)
service.start()

print("Backend démarré. Appuyez sur Ctrl+C pour arrêter.")

try:
    while True:
        input()
except KeyboardInterrupt:
    service.stop()