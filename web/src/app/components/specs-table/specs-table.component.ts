import { Component, Input } from '@angular/core';

import { SpecInfo } from '../../services/package/package.reducer';

@Component({
  selector: 'app-specs-table',
  templateUrl: './specs-table.component.html',
  styleUrls: ['./specs-table.component.css'],
})
export class SpecsTableComponent {
  @Input() specInfos: SpecInfo[] = [];
  displayedColumns: string[] = [
    'id',
    'title',
    'description',
    'version',
    'updated_at',
    'install',
    'model_count',
    'management',
  ];
}
