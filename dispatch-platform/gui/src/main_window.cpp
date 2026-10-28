#include "main_window.hpp"
#include "auth_dialog.hpp"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QSplitter>
#include <QHeaderView>
#include <QDateTime>

MainWindow::MainWindow(QWidget* parent) : QMainWindow(parent) {
    setupUi();
    syncClient = new CloudSyncClient("http://localhost:8765", this);
    localRunner = new LocalRunner(this);

    connect(syncClient, &CloudSyncClient::dispatchCreated, this, &MainWindow::onDispatchCreated);
    connect(syncClient, &CloudSyncClient::localRunCompleted, this, &MainWindow::onSyncFinished);
    connect(localRunner, &LocalRunner::finished, this, &MainWindow::onLocalSolverFinished);

    AuthDialog authDlg("https://your-project.supabase.co", "your_anon_key", this);
    if (authDlg.exec() == QDialog::Accepted) {
        syncClient->setToken(authDlg.getToken());
        userStatusLabel->setText("Connected: " + authDlg.getEmail());
    } else {
        userStatusLabel->setText("Running in Guest / Unauthenticated Mode");
    }
}

void MainWindow::setupUi() {
    resize(1024, 720);
    setWindowTitle("Quantum-Classical Fleet Dispatch Optimizer (NVIDIA & Nebius)");

    auto* central = new QWidget(this);
    setCentralWidget(central);
    auto* mainLayout = new QVBoxLayout(central);

    userStatusLabel = new QLabel(this);
    mainLayout->addWidget(userStatusLabel);

    auto* splitter = new QSplitter(Qt::Horizontal, this);
    mainLayout->addWidget(splitter);

    // Left Control Panel
    auto* leftWidget = new QWidget(this);
    auto* leftLayout = new QVBoxLayout(leftWidget);
    manifestInput = new QTextEdit(this);
    manifestInput->setPlaceholderText("Paste unstructured delivery manifest or stop coordinates here...");

    localGpuRadio = new QRadioButton("Local NVIDIA GPU (CUDA-Q)", this);
    cloudGpuRadio = new QRadioButton("Nebius Cloud Worker (Serverless GPU)", this);
    localGpuRadio->setChecked(true);

    executeBtn = new QPushButton("Run Quantum-Classical Dispatch", this);

    leftLayout->addWidget(new QLabel("Input Delivery Manifest:"));
    leftLayout->addWidget(manifestInput);
    leftLayout->addWidget(new QLabel("Compute Backend:"));
    leftLayout->addWidget(localGpuRadio);
    leftLayout->addWidget(cloudGpuRadio);
    leftLayout->addWidget(executeBtn);
    splitter->addWidget(leftWidget);

    // Right Telemetry Panel
    auto* rightWidget = new QWidget(this);
    auto* rightLayout = new QVBoxLayout(rightWidget);
    logConsole = new QTextEdit(this);
    logConsole->setReadOnly(true);

    metricsTable = new QTableWidget(5, 2, this);
    metricsTable->setHorizontalHeaderLabels(QStringList() << "Metric" << "Value");
    metricsTable->horizontalHeader()->setSectionResizeMode(QHeaderView::Stretch);
    metricsTable->setItem(0, 0, new QTableWidgetItem("Triage Time (Nano)"));
    metricsTable->setItem(1, 0, new QTableWidgetItem("Hamiltonian Time (Ultra)"));
    metricsTable->setItem(2, 0, new QTableWidgetItem("Solver Time (CUDA-Q)"));
    metricsTable->setItem(3, 0, new QTableWidgetItem("Ground Energy"));
    metricsTable->setItem(4, 0, new QTableWidgetItem("Best Bitstring"));

    rightLayout->addWidget(new QLabel("Execution Pipeline Telemetry:"));
    rightLayout->addWidget(logConsole);
    rightLayout->addWidget(metricsTable);
    splitter->addWidget(rightWidget);

    connect(executeBtn, &QPushButton::clicked, this, &MainWindow::onExecuteClicked);
}

void MainWindow::appendLog(const QString& tag, const QString& msg) {
    QString timeStr = QDateTime::currentDateTime().toString("hh:mm:ss.zzz");
    logConsole->append(QString("[%1] <b>%2</b>: %3").arg(timeStr, tag, msg));
}

void MainWindow::onExecuteClicked() {
    QString target = localGpuRadio->isChecked() ? "LOCAL_GPU" : "NEBIUS_CLOUD";
    appendLog("SYSTEM", "Initiating run targeting " + target);
    syncClient->createDispatch("Fleet Optimization Run", manifestInput->toPlainText(), target);
}

void MainWindow::onDispatchCreated(const QJsonObject& data) {
    currentRunId = data["run_id"].toString();
    appendLog("GATEWAY", "Run registered with ID: " + currentRunId);

    auto telem = data["telemetry"].toObject();
    metricsTable->setItem(0, 1, new QTableWidgetItem(QString::number(telem["triage_ms"].toInt()) + " ms"));
    metricsTable->setItem(1, 1, new QTableWidgetItem(QString::number(telem["hamiltonian_ms"].toInt()) + " ms"));

    if (data["status"].toString() == "DELEGATE_LOCAL") {
        appendLog("LOCAL_CUDA-Q", "Starting QAOA state-vector on local NVIDIA hardware...");
        auto hSpec = data["hamiltonian_spec"].toObject();
        localRunner->runQAOA(
            data["graph_data"].toObject(),
            hSpec["p_layers"].toInt(),
            hSpec["gamma_init"].toDouble(),
            hSpec["beta_init"].toDouble()
        );
    } else {
        onSyncFinished(data);
    }
}

void MainWindow::onLocalSolverFinished(const QJsonObject& res) {
    appendLog("LOCAL_CUDA-Q", "Simulation finished. Bitstring: " + res["best_bitstring"].toString());
    metricsTable->setItem(2, 1, new QTableWidgetItem(QString::number(res["solver_latency_ms"].toInt()) + " ms"));
    metricsTable->setItem(3, 1, new QTableWidgetItem(QString::number(res["energy"].toDouble())));
    metricsTable->setItem(4, 1, new QTableWidgetItem(res["best_bitstring"].toString()));

    appendLog("SYNC", "Uploading local metrics to Supabase cloud account...");
    syncClient->completeLocalRun(
        currentRunId,
        res["best_bitstring"].toString(),
        res["solver_latency_ms"].toInt(),
        res["energy"].toDouble()
    );
}

void MainWindow::onSyncFinished(const QJsonObject& data) {
    appendLog("SYNC", "Run synchronized successfully across all authenticated devices.");
}