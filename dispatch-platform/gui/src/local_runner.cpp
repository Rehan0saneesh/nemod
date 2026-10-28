#include "local_runner.hpp"
#include <QJsonDocument>

LocalRunner::LocalRunner(QObject* parent) : QObject(parent), process(new QProcess(this)) {
    connect(process, &QProcess::finished, [this](int exitCode, QProcess::ExitStatus) {
        if (exitCode == 0) {
            auto out = process->readAllStandardOutput();
            emit finished(QJsonDocument::fromJson(out).object());
        } else {
            emit error(process->readAllStandardError());
        }
    });
}

void LocalRunner::runQAOA(const QJsonObject& graphData, int pLayers, double gamma, double beta) {
    QJsonObject payload;
    payload["graph_data"] = graphData;
    payload["p_layers"] = pLayers;
    payload["gamma_init"] = gamma;
    payload["beta_init"] = beta;

    QString scriptPath = "backend/solvers/local_cudaq.py";
    process->start("python3", QStringList() << scriptPath);
    process->write(QJsonDocument(payload).toJson());
    process->closeWriteChannel();
}