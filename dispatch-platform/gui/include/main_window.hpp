#pragma once
#include <QMainWindow>
#include <QTextEdit>
#include <QRadioButton>
#include <QPushButton>
#include <QTableWidget>
#include <QLabel>
#include "cloud_sync.hpp"
#include "local_runner.hpp"

class MainWindow : public QMainWindow {
    Q_OBJECT
public:
    explicit MainWindow(QWidget* parent = nullptr);

private slots:
    void onExecuteClicked();
    void onDispatchCreated(const QJsonObject& data);
    void onLocalSolverFinished(const QJsonObject& res);
    void onSyncFinished(const QJsonObject& data);
    void appendLog(const QString& tag, const QString& msg);

private:
    CloudSyncClient* syncClient;
    LocalRunner* localRunner;
    QString currentRunId;

    QTextEdit* manifestInput;
    QRadioButton* localGpuRadio;
    QRadioButton* cloudGpuRadio;
    QPushButton* executeBtn;
    QTextEdit* logConsole;
    QTableWidget* metricsTable;
    QLabel* userStatusLabel;

    void setupUi();
};