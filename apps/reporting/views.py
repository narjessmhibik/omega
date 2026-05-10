# apps/reporting/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
import io

from apps.accounts.models import User
from apps.interventions.models import Intervention
from apps.interventions.models import BaremeTechnicien, BaremeOperateur
from apps.accounts.permissions import IsAdmin

# Imports pour exports
try:
    from openpyxl import Workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


# ✅ Nom exact du statut "Réussie" en base
STATUT_REUSSIE = 'Réussie'


def est_reussie(intervention):
    """Retourne True si l'intervention est Réussie"""
    return intervention.statut and intervention.statut.nom == STATUT_REUSSIE


def get_ca_client(intervention):
    """Calcule le CA client à partir du barème opérateur"""
    if intervention.operateur and intervention.type_intervention:
        try:
            bareme = BaremeOperateur.objects.get(
                operateur=intervention.operateur,
                type_intervention=intervention.type_intervention
            )
            return float(bareme.prix)
        except BaremeOperateur.DoesNotExist:
            pass
    return 0.0


def get_cout_technicien(intervention):
    """Calcule le coût technicien à partir du barème technicien"""
    if intervention.type_intervention:
        try:
            bareme = BaremeTechnicien.objects.get(
                type_intervention=intervention.type_intervention
            )
            return float(bareme.prix)
        except BaremeTechnicien.DoesNotExist:
            pass
    return 0.0


class DashboardAdminView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        aujourd_hui = timezone.now()
        debut_mois = aujourd_hui.replace(day=1, hour=0, minute=0, second=0)

        # Toutes les interventions du mois (pour le compteur)
        toutes = Intervention.objects.filter(
            date_intervention__gte=debut_mois
        )

        # ✅ Seulement les Réussies pour CA et coûts
        reussies = toutes.filter(statut__nom=STATUT_REUSSIE)

        total_ca = 0.0
        total_cout = 0.0

        for inv in reussies:
            total_ca += get_ca_client(inv)
            total_cout += get_cout_technicien(inv)

        total_marge = total_ca - total_cout

        return Response({
            'periode': debut_mois.strftime('%B %Y'),
            'nb_interventions': toutes.count(),
            'chiffre_affaires': total_ca,
            'couts_techniciens': total_cout,
            'marge_brute': total_marge,
            'taux_marge': round(total_marge / total_ca * 100, 2) if total_ca else 0,
        })


class StatsTechnicienView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        try:
            aujourd_hui = timezone.now()
            debut_mois = aujourd_hui.replace(day=1, hour=0, minute=0, second=0)

            techniciens = User.objects.filter(role='technicien', est_actif=True)
            result = []

            for tech in techniciens:
                # Toutes les interventions du mois pour ce technicien
                toutes = Intervention.objects.filter(
                    technicien=tech,
                    date_intervention__gte=debut_mois
                )
                # ✅ Seulement les Réussies pour CA et gains
                reussies = toutes.filter(statut__nom=STATUT_REUSSIE)

                ca_total = 0.0
                cout_total = 0.0

                for inv in reussies:
                    ca_total += get_ca_client(inv)
                    cout_total += get_cout_technicien(inv)

                result.append({
                    'technicien_id': tech.id,
                    'technicien_nom': tech.get_full_name() or tech.username,
                    'nb_interventions': toutes.count(),
                    'nb_reussies': reussies.count(),
                    'chiffre_affaires': ca_total,
                    'gains': cout_total,
                    'marge_generee': ca_total - cout_total,
                })

            result.sort(key=lambda x: x['chiffre_affaires'], reverse=True)
            return Response(result)

        except Exception as e:
            print(f"Erreur StatsTechnicienView: {str(e)}")
            return Response({'error': str(e)}, status=500)


class MonDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        aujourd_hui = timezone.now()
        debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        debut_mois = aujourd_hui.replace(day=1, hour=0, minute=0, second=0)

        def stats_periode(debut):
            toutes = Intervention.objects.filter(
                technicien=user,
                date_intervention__gte=debut
            )
            # ✅ Gains uniquement sur les Réussies
            reussies = toutes.filter(statut__nom=STATUT_REUSSIE)

            gains = 0.0
            for inv in reussies:
                gains += get_cout_technicien(inv)

            return {
                'nb_interventions': toutes.count(),
                'gains': gains,
            }

        ce_mois = stats_periode(debut_mois)

        return Response({
            'technicien': user.get_full_name(),
            'periode': debut_mois.strftime('%B %Y'),
            'gains': ce_mois['gains'],
            'nb_interventions': ce_mois['nb_interventions'],
            'aujourd_hui': stats_periode(aujourd_hui.replace(hour=0, minute=0, second=0)),
            'cette_semaine': stats_periode(debut_semaine),
            'ce_mois': ce_mois,
        })


class HistoriqueInterventionsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        interventions = Intervention.objects.all()

        technicien_id = request.query_params.get('technicien_id')
        mois = request.query_params.get('mois')

        if technicien_id:
            interventions = interventions.filter(technicien_id=technicien_id)

        if mois:
            try:
                annee, mois_num = mois.split('-')
                interventions = interventions.filter(
                    date_intervention__year=annee,
                    date_intervention__month=mois_num
                )
            except:
                pass

        result = []
        for inv in interventions:
            # ✅ CA et gain seulement si Réussie
            reussie = est_reussie(inv)
            ca = get_ca_client(inv) if reussie else 0.0
            cout = get_cout_technicien(inv) if reussie else 0.0

            result.append({
                'id': inv.id,
                'technicien': inv.technicien.get_full_name() if inv.technicien else "-",
                'ticket_id': inv.ticket_id or "-",
                'operateur': inv.operateur.nom if inv.operateur else "-",
                'type_intervention': inv.type_intervention.nom if inv.type_intervention else "-",
                'statut': inv.statut.nom if inv.statut else "-",
                'adresse': inv.adresse or "-",
                'ville': inv.ville or "-",
                'date': inv.date_intervention.strftime('%d/%m/%Y %H:%M') if inv.date_intervention else "-",
                'ca': ca,
                'gain_technicien': cout,
                'marge': ca - cout,
            })

        return Response({
            'nb_resultats': len(result),
            'interventions': result
        })


class ExportExcelView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        if not OPENPYXL_AVAILABLE:
            return Response({'error': 'openpyxl non installé'}, status=500)

        try:
            interventions = Intervention.objects.all().order_by('-date_intervention')

            wb = Workbook()
            ws = wb.active
            ws.title = "Interventions"

            headers = [
                'N°', 'Ticket', 'Technicien', 'Opérateur', 'Type',
                'Adresse', 'Ville', 'Date', 'Statut', 'CA (€)', 'Gain Tech (€)', 'Marge (€)'
            ]
            ws.append(headers)

            for index, inv in enumerate(interventions, start=1):
                # ✅ CA et gain seulement si Réussie
                reussie = est_reussie(inv)
                ca = get_ca_client(inv) if reussie else 0.0
                cout = get_cout_technicien(inv) if reussie else 0.0

                ws.append([
                    index,
                    inv.ticket_id or "-",
                    inv.technicien.get_full_name() if inv.technicien else "-",
                    inv.operateur.nom if inv.operateur else "-",
                    inv.type_intervention.nom if inv.type_intervention else "-",
                    inv.adresse or "-",
                    inv.ville or "-",
                    inv.date_intervention.strftime('%d/%m/%Y %H:%M') if inv.date_intervention else "-",
                    inv.statut.nom if inv.statut else "-",
                    ca,
                    cout,
                    ca - cout
                ])

            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="interventions_export.xlsx"'
            wb.save(response)
            return response

        except Exception as e:
            print(f"Erreur ExportExcel: {str(e)}")
            return Response({'error': str(e)}, status=500)


class ExportPDFView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        if not REPORTLAB_AVAILABLE:
            return Response({'error': 'reportlab non installé'}, status=500)

        try:
            interventions = Intervention.objects.all().order_by('-date_intervention')[:100]

            buffer = io.BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4

            p.setFont("Helvetica-Bold", 16)
            p.drawString(50, height - 50, "OMEGA - Rapport des interventions")

            p.setFont("Helvetica", 10)
            p.drawString(50, height - 70, f"Généré le : {timezone.now().strftime('%d/%m/%Y à %H:%M')}")

            p.setFont("Helvetica-Bold", 9)
            y = height - 100
            p.drawString(30, y, "N°")
            p.drawString(60, y, "Ticket")
            p.drawString(120, y, "Technicien")
            p.drawString(200, y, "Type")
            p.drawString(270, y, "Statut")
            p.drawString(340, y, "Date")
            p.drawString(410, y, "CA (€)")
            p.drawString(460, y, "Gain (€)")

            p.line(30, y - 5, 550, y - 5)
            p.setFont("Helvetica", 8)
            y -= 20

            for index, inv in enumerate(interventions, start=1):
                if y < 50:
                    p.showPage()
                    y = height - 50
                    p.setFont("Helvetica-Bold", 9)
                    p.drawString(30, y, "N°")
                    p.drawString(60, y, "Ticket")
                    p.drawString(120, y, "Technicien")
                    p.drawString(200, y, "Type")
                    p.drawString(270, y, "Statut")
                    p.drawString(340, y, "Date")
                    p.drawString(410, y, "CA (€)")
                    p.drawString(460, y, "Gain (€)")
                    p.line(30, y - 5, 550, y - 5)
                    p.setFont("Helvetica", 8)
                    y -= 20

                # ✅ CA et gain seulement si Réussie
                reussie = est_reussie(inv)
                ca = get_ca_client(inv) if reussie else 0.0
                cout = get_cout_technicien(inv) if reussie else 0.0
                statut_nom = inv.statut.nom if inv.statut else "-"

                p.drawString(30, y, str(index))
                p.drawString(60, y, str(inv.ticket_id or "-")[:12])
                p.drawString(120, y, (inv.technicien.get_full_name() if inv.technicien else "-")[:14])
                p.drawString(200, y, (inv.type_intervention.nom if inv.type_intervention else "-")[:12])
                p.drawString(270, y, statut_nom[:14])
                p.drawString(340, y, inv.date_intervention.strftime('%d/%m/%Y') if inv.date_intervention else "-")
                p.drawString(410, y, f"{ca:.2f}")
                p.drawString(460, y, f"{cout:.2f}")

                y -= 15

            p.save()
            buffer.seek(0)

            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="interventions_export.pdf"'
            return response

        except Exception as e:
            print(f"Erreur ExportPDF: {str(e)}")
            return Response({'error': str(e)}, status=500)
        

class HistoriqueMensuelView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        interventions = Intervention.objects.all().order_by('-date_intervention')
        
        mois_dict = {}
        for inv in interventions:
            if not inv.date_intervention:
                continue
            cle = inv.date_intervention.strftime('%Y-%m')
            label = inv.date_intervention.strftime('%B %Y')
            
            if cle not in mois_dict:
                mois_dict[cle] = {
                    'mois': cle,
                    'label': label,
                    'nb_interventions': 0,
                    'nb_reussies': 0,
                    'ca': 0.0,
                    'couts': 0.0,
                    'marge': 0.0,
                }
            
            mois_dict[cle]['nb_interventions'] += 1
            reussie = est_reussie(inv)
            if reussie:
                ca = get_ca_client(inv)
                cout = get_cout_technicien(inv)
                mois_dict[cle]['nb_reussies'] += 1
                mois_dict[cle]['ca'] += ca
                mois_dict[cle]['couts'] += cout
                mois_dict[cle]['marge'] += ca - cout

        result = sorted(mois_dict.values(), key=lambda x: x['mois'], reverse=True)
        return Response(result)


class ExportExcelMoisView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, mois):
        if not OPENPYXL_AVAILABLE:
            return Response({'error': 'openpyxl non installé'}, status=500)
        try:
            annee, mois_num = mois.split('-')
            interventions = Intervention.objects.filter(
                date_intervention__year=annee,
                date_intervention__month=mois_num
            ).order_by('-date_intervention')

            wb = Workbook()
            ws = wb.active
            ws.title = f"Mois {mois}"

            headers = ['N°', 'Ticket', 'Technicien', 'Opérateur', 'Type',
                      'Date', 'Statut', 'CA (€)', 'Gain Tech (€)', 'Marge (€)']
            ws.append(headers)

            for index, inv in enumerate(interventions, start=1):
                reussie = est_reussie(inv)
                ca = get_ca_client(inv) if reussie else 0.0
                cout = get_cout_technicien(inv) if reussie else 0.0
                ws.append([
                    index,
                    inv.ticket_id or "-",
                    inv.technicien.get_full_name() if inv.technicien else "-",
                    inv.operateur.nom if inv.operateur else "-",
                    inv.type_intervention.nom if inv.type_intervention else "-",
                    inv.date_intervention.strftime('%d/%m/%Y') if inv.date_intervention else "-",
                    inv.statut.nom if inv.statut else "-",
                    ca, cout, ca - cout
                ])

            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="omega_{mois}.xlsx"'
            wb.save(response)
            return response
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        

class HistoriqueMensuelTechView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        interventions = Intervention.objects.filter(
            technicien=request.user
        ).order_by('-date_intervention')

        mois_dict = {}
        for inv in interventions:
            if not inv.date_intervention:
                continue
            cle = inv.date_intervention.strftime('%Y-%m')
            label = inv.date_intervention.strftime('%B %Y')

            if cle not in mois_dict:
                mois_dict[cle] = {
                    'mois': cle,
                    'label': label,
                    'nb_interventions': 0,
                    'nb_reussies': 0,
                    'gains': 0.0,
                }

            mois_dict[cle]['nb_interventions'] += 1
            if est_reussie(inv):
                mois_dict[cle]['nb_reussies'] += 1
                mois_dict[cle]['gains'] += get_cout_technicien(inv)

        result = sorted(mois_dict.values(), key=lambda x: x['mois'], reverse=True)
        return Response(result)