#pragma once
#include <QObject>
#include <QNetworkAccessManager>
#include <QJsonObject>

class CloudSyncClient : public QObject {
    Q_OBJECT
public:
    explicit CloudSyncClient(const QString& gatewayUrl, QObject* parent = nullptr);
    void setToken(const QString& token);
    void createDispatch(const QString& title, const QString& manifest, const QString& target);
    void completeLocalRun(const QString& runId, const QString& bitstring, int latencyMs, double energy);

signals:
    void dispatchCreated(const QJsonObject& data);
    void localRunCompleted(const QJsonObject& data);
    void errorOccurred(const QString& message);

private:
    QString gatewayUrl;
    QString token;
    QNetworkAccessManager* net;
};