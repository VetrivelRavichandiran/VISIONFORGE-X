"""VISIONFORGE X - Report Generation Module."""
import os
import json
import csv
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    report_type: str  # benchmark | system | experiment | event_summary
    title: str
    include_metadata: bool = True
    include_benchmark: bool = False
    include_events: bool = False
    include_fpga: bool = False
    include_confusion_matrix: bool = False
    benchmark_session_ids: List[int] = None
    event_filters: Dict = None


class ReportGenerator:
    """Generates reports in PDF, CSV, and JSON formats."""

    def __init__(self, db_manager=None, event_manager=None, benchmark_runner=None):
        self._db = db_manager
        self._event_mgr = event_manager
        self._benchmark = benchmark_runner
        self._output_dir = "./storage/reports"
        os.makedirs(self._output_dir, exist_ok=True)

    def generate(self, config: ReportConfig) -> Dict[str, str]:
        """Generate report in all available formats. Returns paths."""
        data = self._collect_data(config)
        paths = {}

        # JSON export
        json_path = self._export_json(data, config)
        if json_path:
            paths['json'] = json_path

        # CSV export
        csv_path = self._export_csv(data, config)
        if csv_path:
            paths['csv'] = csv_path

        # PDF export
        pdf_path = self._export_pdf(data, config)
        if pdf_path:
            paths['pdf'] = pdf_path

        # Log to database
        if self._db:
            try:
                summary = f"Type: {config.report_type}, Formats: {list(paths.keys())}"
                self._db.log_report(
                    config.report_type, config.title,
                    list(paths.values())[0] if paths else "", summary
                )
            except Exception as e:
                logger.error(f"Failed to log report: {e}")

        return paths

    def _collect_data(self, config: ReportConfig) -> Dict[str, Any]:
        """Collect data for the report."""
        data = {
            'report_title': config.title,
            'report_type': config.report_type,
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'data_sources': [],
        }

        if config.include_metadata:
            data['metadata'] = {
                'platform': 'VISIONFORGE X',
                'version': '1.0.0',
                'generator': 'ReportGenerator',
            }
            data['data_sources'].append('metadata')

        if config.include_benchmark and self._benchmark:
            benchmark_data = []
            for sid in (config.benchmark_session_ids or []):
                result = self._benchmark.get_session_results(sid)
                if result:
                    benchmark_data.append(result)
            data['benchmark'] = {
                'sessions': benchmark_data,
                'is_simulated': any(
                    s.get('is_simulated', False) for s in benchmark_data
                ),
            }
            data['data_sources'].append('benchmark')

        if config.include_events and self._event_mgr:
            events = self._event_mgr.get_events(
                limit=1000,
                category=config.event_filters.get('category') if config.event_filters else None,
                severity=config.event_filters.get('severity') if config.event_filters else None,
            )
            data['events'] = [e.to_dict() for e in events]
            data['data_sources'].append('events')

        if config.include_fpga and self._db:
            fpga_data = self._db.query(
                "SELECT DISTINCT device_name, bitstream_version FROM telemetry_samples LIMIT 10"
            )
            data['fpga'] = {'device_info': fpga_data}
            data['data_sources'].append('fpga')

        return data

    def _export_json(self, data: Dict, config: ReportConfig) -> Optional[str]:
        """Export report as JSON."""
        try:
            filename = f"report_{config.report_type}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
            path = os.path.join(self._output_dir, filename)
            with open(path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"JSON report exported: {path}")
            return path
        except (IOError, OSError) as e:
            logger.error(f"JSON export failed: {e}")
            return None

    def _export_csv(self, data: Dict, config: ReportConfig) -> Optional[str]:
        """Export report data as CSV."""
        try:
            filename = f"report_{config.report_type}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
            path = os.path.join(self._output_dir, filename)

            with open(path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Field', 'Value', 'Source', 'Notes'])
                writer.writerow(['Report Title', data['report_title'], 'metadata', ''])
                writer.writerow(['Report Type', data['report_type'], 'metadata', ''])
                writer.writerow(['Generated At', data['generated_at'], 'metadata', ''])

                if 'benchmark' in data:
                    for session in data['benchmark'].get('sessions', []):
                        for metric, values in session.get('metrics', {}).items():
                            if isinstance(values, dict):
                                for k, v in values.items():
                                    writer.writerow(
                                        [f"benchmark.{session.get('name','')}.{metric}.{k}",
                                         v, 'benchmark',
                                         'SIMULATED' if session.get('is_simulated') else 'MEASURED']
                                    )

                if 'events' in data:
                    for event in data['events']:
                        writer.writerow(
                            [f"event.{event.get('category','')}",
                             event.get('description', ''), 'events', '']
                        )

            logger.info(f"CSV report exported: {path}")
            return path
        except (IOError, OSError) as e:
            logger.error(f"CSV export failed: {e}")
            return None

    def _export_pdf(self, data: Dict, config: ReportConfig) -> Optional[str]:
        """Export report as PDF using ReportLab."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.enums import TA_CENTER, TA_LEFT

            filename = f"report_{config.report_type}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.pdf"
            path = os.path.join(self._output_dir, filename)

            doc = SimpleDocTemplate(path, pagesize=A4,
                                    rightMargin=0.75*inch, leftMargin=0.75*inch,
                                    topMargin=0.75*inch, bottomMargin=0.75*inch)
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle', parent=styles['Title'],
                fontSize=18, textColor=colors.HexColor('#00E5FF'),
                spaceAfter=12, alignment=TA_CENTER
            )
            heading_style = ParagraphStyle(
                'CustomHeading', parent=styles['Heading2'],
                fontSize=14, textColor=colors.HexColor('#00E5FF'),
                spaceAfter=8
            )
            body_style = ParagraphStyle(
                'CustomBody', parent=styles['BodyText'],
                fontSize=10, spaceAfter=6
            )

            story = []

            # Title
            story.append(Paragraph(config.title, title_style))
            story.append(Paragraph(
                f"Generated: {data['generated_at']} | Type: {data['report_type']}",
                ParagraphStyle('Meta', parent=body_style, alignment=TA_CENTER, fontSize=9)
            ))
            story.append(Spacer(1, 12))

            # Metadata
            if 'metadata' in data:
                story.append(Paragraph("Platform Information", heading_style))
                meta = data['metadata']
                meta_data = [[k, v] for k, v in meta.items()]
                t = Table(meta_data, colWidths=[2*inch, 4*inch])
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1E272E')),
                    ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#3D4A5A')),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                ]))
                story.append(t)
                story.append(Spacer(1, 12))

            # Benchmark results
            if 'benchmark' in data:
                story.append(Paragraph("Benchmark Results", heading_style))
                note = "(SIMULATED)" if data['benchmark'].get('is_simulated') else "(MEASURED)"
                story.append(Paragraph(f"Data source: {note}", body_style))
                for session in data['benchmark'].get('sessions', []):
                    story.append(Paragraph(f"  Session: {session.get('name', 'N/A')}", body_style))
                    story.append(Paragraph(
                        f"  Duration: {session.get('duration_seconds', 'N/A')}s | Mode: {session.get('mode', 'N/A')}",
                        body_style
                    ))
                    for metric, values in session.get('metrics', {}).items():
                        if isinstance(values, dict):
                            metric_row = [
                                [metric, 'Avg', 'Min', 'Max', 'Median', 'P95'],
                                ['',
                                 f"{values.get('avg', 0):.2f}",
                                 f"{values.get('min', 0):.2f}",
                                 f"{values.get('max', 0):.2f}",
                                 f"{values.get('median', 0):.2f}",
                                 f"{values.get('p95', 0):.2f}"]
                            ]
                            mt = Table(metric_row, colWidths=[1.5*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch, 0.9*inch])
                            mt.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E272E')),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#00E5FF')),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#3D4A5A')),
                                ('FONTSIZE', (0, 0), (-1, -1), 8),
                                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                            ]))
                            story.append(mt)
                            story.append(Spacer(1, 8))
                story.append(Spacer(1, 12))

            # Event summary
            if 'events' in data:
                events = data['events']
                story.append(Paragraph("Event Summary", heading_style))
                story.append(Paragraph(f"Total events: {len(events)}", body_style))
                # Count by category
                cat_counts = {}
                for e in events:
                    cat = e.get('category', 'unknown')
                    cat_counts[cat] = cat_counts.get(cat, 0) + 1
                cat_data = [[k, v] for k, v in sorted(cat_counts.items(), key=lambda x: -x[1])]
                if cat_data:
                    ct = Table(cat_data, colWidths=[3*inch, 3*inch])
                    ct.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1E272E')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#3D4A5A')),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ]))
                    story.append(ct)

            # Data sources note
            story.append(Spacer(1, 12))
            story.append(Paragraph(
                f"Data sources included: {', '.join(data.get('data_sources', []))}",
                ParagraphStyle('Note', parent=body_style, fontSize=8, textColor=colors.grey)
            ))

            doc.build(story)
            logger.info(f"PDF report exported: {path}")
            return path
        except ImportError:
            logger.warning("ReportLab not available, skipping PDF export")
            return None
        except (IOError, OSError) as e:
            logger.error(f"PDF export failed: {e}")
            return None
