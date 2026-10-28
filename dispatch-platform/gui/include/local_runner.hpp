#pragma once
#include <QObject>
#include <QProcess>
#include <QJsonObject>

class LocalRunner : public QObject {
    Q_OBJECT
public:
    explicit LocalRunner(QObject* parent = nullptr);
    void runQAOA(const QJsonObject& graphData, int pLayers, double gamma, double beta);

signals:
    void finished(const QJsonObject& result);
    void error(const QString& err);

private:
    QProcess* process;
};