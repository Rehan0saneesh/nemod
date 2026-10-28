#pragma once
#include <QDialog>
#include <QLineEdit>
#include <QPushButton>
#include <QNetworkAccessManager>

class AuthDialog : public QDialog {
    Q_OBJECT
public:
    explicit AuthDialog(const QString& supabaseUrl, const QString& anonKey, QWidget* parent = nullptr);
    QString getToken() const;
    QString getEmail() const;

private slots:
    void handleLogin();
    void handleRegister();

private:
    QString supabaseUrl;
    QString anonKey;
    QString jwtToken;
    QString userEmail;
    QLineEdit* emailEdit;
    QLineEdit* passwordEdit;
    QPushButton* loginBtn;
    QPushButton* registerBtn;
    QNetworkAccessManager* net;

    void performAuth(const QString& endpoint);
};