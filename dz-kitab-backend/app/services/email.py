# app/services/email.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import os

# Configuration Email
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "your-email@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your-app-password")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@dz-kitab.com")

def send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None):
    """
    Envoyer un email HTML/texte
    
    Args:
        to_email: Email du destinataire
        subject: Sujet de l'email
        html_content: Contenu HTML
        text_content: Contenu texte alternatif
    """
    try:
        # Crer le message
        message = MIMEMultipart("alternative")
        message["From"] = FROM_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        
        # Ajouter le contenu texte si fourni
        if text_content:
            part1 = MIMEText(text_content, "plain", "utf-8")
            message.attach(part1)
        
        # Ajouter le contenu HTML
        part2 = MIMEText(html_content, "html", "utf-8")
        message.attach(part2)
        
        # Envoyer l'email
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(message)
        
        print(f" Email envoy  {to_email}")
        return True
        
    except Exception as e:
        print(f" Erreur envoi email  {to_email}: {e}")
        return False


def send_low_rating_alert(seller_email: str, seller_name: str, low_rating_count: int, average_rating: float):
    """
    Envoyer une alerte au vendeur pour notes basses
    
    Args:
        seller_email: Email du vendeur
        seller_name: Nom du vendeur
        low_rating_count: Nombre de notes de 1 toile
        average_rating: Note moyenne actuelle
    """
    subject = " Alerte : Vos valuations ncessitent votre attention"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #f44336; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; }}
            .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; }}
            .stats {{ background: white; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .cta {{ background: #2196F3; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1> Alerte Qualit de Service</h1>
            </div>
            <div class="content">
                <p>Bonjour <strong>{seller_name}</strong>,</p>
                
                <div class="warning">
                    <strong> Attention :</strong> Vous avez reu <strong>{low_rating_count} valuations ngatives</strong> (1 toile ou moins) rcemment.
                </div>
                
                <div class="stats">
                    <h3>Vos statistiques actuelles :</h3>
                    <ul>
                        <li> Note moyenne : <strong>{average_rating:.2f}/5.0</strong></li>
                        <li> Notes de 1 toile : <strong>{low_rating_count}</strong></li>
                    </ul>
                </div>
                
                <h3> Que devez-vous faire ?</h3>
                <ol>
                    <li><strong>Analysez les commentaires</strong> : Lisez attentivement les retours ngatifs</li>
                    <li><strong>Amliorez votre service</strong> :
                        <ul>
                            <li>Vrifiez l'tat des livres avant la vente</li>
                            <li>Soyez transparent sur l'tat du livre</li>
                            <li>Communiquez rapidement avec les acheteurs</li>
                            <li>Respectez vos engagements de livraison</li>
                        </ul>
                    </li>
                    <li><strong>Contactez les acheteurs mcontents</strong> si possible</li>
                </ol>
                
                <div class="warning">
                    <strong> Important :</strong> Si vous atteignez <strong>10 valuations  0 toile</strong>, votre compte sera automatiquement <strong>suspendu pendant 15 jours</strong>.
                </div>
                
                <center>
                    <a href="http://localhost:3000/profile/ratings" class="cta"> Voir mes valuations</a>
                </center>
                
                <p>Nous sommes l pour vous aider  russir sur DZ-Kitab. N'hsitez pas  consulter nos guides de bonnes pratiques.</p>
                
                <p>Cordialement,<br><strong>L'quipe DZ-Kitab</strong></p>
            </div>
            
            <div class="footer">
                <p>DZ-Kitab - Plateforme d'change de livres universitaires</p>
                <p>Cet email a t envoy automatiquement, merci de ne pas y rpondre.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Alerte Qualit de Service - DZ-Kitab
    
    Bonjour {seller_name},
    
    Vous avez reu {low_rating_count} valuations ngatives (1 toile ou moins).
    Note moyenne actuelle : {average_rating:.2f}/5.0
    
    Que faire ?
    1. Analysez les commentaires ngatifs
    2. Amliorez votre service
    3. Contactez les acheteurs mcontents
    
    ATTENTION : 10 notes  0 toile = suspension 15 jours
    
    Consultez vos valuations : http://localhost:3000/profile/ratings
    
    L'quipe DZ-Kitab
    """
    
    return send_email(seller_email, subject, html_content, text_content)


def send_account_suspension_notice(seller_email: str, seller_name: str, zero_rating_count: int, suspension_end_date: str):
    """
    Notifier le vendeur de la suspension de son compte
    
    Args:
        seller_email: Email du vendeur
        seller_name: Nom du vendeur
        zero_rating_count: Nombre de notes  0
        suspension_end_date: Date de fin de suspension
    """
    subject = " Suspension de votre compte DZ-Kitab - 15 jours"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #d32f2f; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; }}
            .alert {{ background: #ffebee; border-left: 4px solid #d32f2f; padding: 15px; margin: 20px 0; }}
            .info-box {{ background: white; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .date {{ background: #fff59d; padding: 10px; border-radius: 5px; text-align: center; font-size: 18px; font-weight: bold; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1> Suspension de Compte</h1>
            </div>
            <div class="content">
                <p>Bonjour <strong>{seller_name}</strong>,</p>
                
                <div class="alert">
                    <h2> Votre compte a t suspendu</h2>
                    <p>En raison de <strong>{zero_rating_count} valuations  0 toile</strong>, votre compte vendeur a t automatiquement suspendu pour une dure de <strong>15 jours</strong>.</p>
                </div>
                
                <div class="info-box">
                    <h3> Date de ractivation :</h3>
                    <div class="date">{suspension_end_date}</div>
                </div>
                
                <div class="info-box">
                    <h3> Pendant la suspension :</h3>
                    <ul>
                        <li> Vous ne pouvez <strong>pas crer</strong> de nouvelles annonces</li>
                        <li> Vos annonces existantes sont <strong>dsactives</strong></li>
                        <li> Vous pouvez <strong>consulter</strong> votre compte</li>
                        <li> Vous pouvez <strong>lire</strong> vos valuations</li>
                    </ul>
                </div>
                
                <div class="info-box">
                    <h3> Aprs la suspension :</h3>
                    <ol>
                        <li>Votre compte sera <strong>automatiquement ractiv</strong> le {suspension_end_date}</li>
                        <li>Vous recevrez un email de confirmation</li>
                        <li>Vous pourrez  nouveau publier des annonces</li>
                        <li><strong>Amliorez votre service</strong> pour viter une nouvelle suspension</li>
                    </ol>
                </div>
                
                <div class="alert">
                    <h3> Recommandations :</h3>
                    <ul>
                        <li>Lisez <strong>attentivement</strong> tous les commentaires ngatifs</li>
                        <li>Identifiez les <strong>problmes rcurrents</strong></li>
                        <li>Consultez notre <strong>guide des bonnes pratiques</strong></li>
                        <li>En cas de question, contactez notre support</li>
                    </ul>
                </div>
                
                <p>Nous esprons que cette priode vous permettra d'amliorer la qualit de votre service.</p>
                
                <p>Cordialement,<br><strong>L'quipe DZ-Kitab</strong></p>
            </div>
            
            <div class="footer">
                <p>DZ-Kitab - Plateforme d'change de livres universitaires</p>
                <p>Email automatique - Support : support@dz-kitab.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Suspension de Compte - DZ-Kitab
    
    Bonjour {seller_name},
    
    VOTRE COMPTE A T SUSPENDU
    
    Raison : {zero_rating_count} valuations  0 toile
    Dure : 15 jours
    Ractivation : {suspension_end_date}
    
    Pendant la suspension :
    - Impossible de crer des annonces
    - Annonces existantes dsactives
    - Consultation du compte autorise
    
    Aprs la suspension :
    - Ractivation automatique le {suspension_end_date}
    - Email de confirmation
    - Possibilit de publier  nouveau
    
    Amliorez votre service pour viter une nouvelle suspension.
    
    L'quipe DZ-Kitab
    Support : support@dz-kitab.com
    """
    
    return send_email(seller_email, subject, html_content, text_content)


def send_account_reactivation_notice(seller_email: str, seller_name: str):
    """
    Notifier le vendeur de la ractivation de son compte
    """
    subject = " Ractivation de votre compte DZ-Kitab"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #4caf50; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; }}
            .success {{ background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; }}
            .cta {{ background: #2196F3; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }}
            .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1> Compte Ractiv</h1>
            </div>
            <div class="content">
                <p>Bonjour <strong>{seller_name}</strong>,</p>
                
                <div class="success">
                    <h2> Bonne nouvelle !</h2>
                    <p>Votre priode de suspension de 15 jours est termine. Votre compte est maintenant <strong>ractiv</strong>.</p>
                </div>
                
                <h3> Vous pouvez  nouveau :</h3>
                <ul>
                    <li>Crer de nouvelles annonces</li>
                    <li>Ractiver vos anciennes annonces</li>
                    <li>Vendre vos livres</li>
                </ul>
                
                <h3> Conseils pour russir :</h3>
                <ul>
                    <li>Dcrivez prcisment l'tat de vos livres</li>
                    <li>Utilisez le systme d'valuation de l'tat</li>
                    <li>Rpondez rapidement aux messages</li>
                    <li>Respectez vos engagements</li>
                </ul>
                
                <center>
                    <a href="http://localhost:3000/dashboard" class="cta"> Accder  mon compte</a>
                </center>
                
                <p>Merci de votre comprhension et bonne vente !</p>
                
                <p>Cordialement,<br><strong>L'quipe DZ-Kitab</strong></p>
            </div>
            
            <div class="footer">
                <p>DZ-Kitab - Plateforme d'change de livres universitaires</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(seller_email, subject, html_content)
