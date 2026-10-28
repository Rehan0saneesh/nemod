#include "auth_dialog.hpp"
#include <QVBoxLayout>
#include <QLabel>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QJsonDocument>
#include <QJsonObject>
#include <QMessageBox>

AuthDialog::AuthDialog(const QString& url, const QString& key, QWidget* parent)
    : QDialog(parent), supabaseUrl(url), anonKey(key), net(new QNetworkAccessManager(this)) {
    setWindowTitle("Supabase Cloud Authentication");
    resize(360, 200);

    auto* layout = new QVBoxLayout(this);
    emailEdit = new QLineEdit(this);
    emailEdit->setPlaceholderText("Email address");
    passwordEdit = new QLineEdit(this);
    passwordEdit->setPlaceholderText("Password");
    passwordEdit->setEchoMode(QLineEdit::Password);

    loginBtn = new QPushButton("Log In", this);
    registerBtn = new QPushButton("Register", this);

    layout->addWidget(new QLabel("Sign in to sync runs across devices:"));
    layout->addWidget(emailEdit);
    layout->addWidget(passwordEdit);
    layout->addWidget(loginBtn);
    layout->addWidget(registerBtn);

    connect(loginBtn, &QPushButton::clicked, this, &AuthDialog::handleLogin);
    connect(registerBtn, &QPushButton::clicked, this, &AuthDialog::handleRegister);
}

QString AuthDialog::getToken() const { return jwtToken; }
QString AuthDialog::getEmail() const { return userEmail; }

void AuthDialog::handleLogin() { performAuth("/auth/v1/token?grant_type=password"); }
void AuthDialog::handleRegister() { performAuth("/auth/v1/signup"); }

void AuthDialog::performAuth(const QString& endpoint) {
    QUrl url(supabaseUrl + endpoint);
    QNetworkRequest request(url);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setRawHeader("apikey", anonKey.toUtf8());

    QJsonObject body;
    body["email"] = emailEdit->text().trimmed();
    body["password"] = passwordEdit->text();

    QNetworkReply* reply = net->post(request, QJsonDocument(body).toJson());
    connect(reply, &QNetworkReply::finished, [this, reply]() {
        if (reply->error() == QNetworkReply::NoError) {
            auto doc = QJsonDocument::fromJson(reply->readAll());
            jwtToken = doc.object()["access_token"].toString();
            userEmail = emailEdit->text().trimmed();
            QMessageBox::information(this, "Success", "Authenticated successfully.");
            accept();
        } else {
            QMessageBox::warning(this, "Authentication Failed", reply->readAll());
        }
        reply->deleteLater();
    });
}