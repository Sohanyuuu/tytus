import { Component, OnInit } from '@angular/core';
import {FlatTreeControl} from '@angular/cdk/tree';
import {MatTreeFlatDataSource, MatTreeFlattener} from '@angular/material/tree';

interface DBNode {
  name: string;
  children?: DBNode[];
}

const DATA: DBNode[] = [
  {
    name: 'Server',
    children: [
      {name: 'Tytus',
      children: [
        {name: 'Databases',
        children: [
          {name:'Database1'}
        ]},
        {name: 'Login/Groups'},
        {name: 'TableSpaces'}
      ]}
    ]
  }
];

interface FlatNode {
  expandable: boolean;
  name: string;
  level: number;
}

@Component({
  selector: 'app-tree',
  templateUrl: './tree.component.html',
  styleUrls: ['./tree.component.css']
})
export class TreeComponent implements OnInit {

  private _transformer = (node: DBNode, level: number) => {
    return {
      expandable: !!node.children && node.children.length > 0,
      name: node.name,
      level: level,
    };
  }

  treeControl = new FlatTreeControl<FlatNode>(
      node => node.level, node => node.expandable);

  treeFlattener = new MatTreeFlattener(
      this._transformer, node => node.level, node => node.expandable, node => node.children);

  dataSource = new MatTreeFlatDataSource(this.treeControl, this.treeFlattener);

  constructor() {
    this.dataSource.data = DATA;
  }

  hasChild = (_: number, node: FlatNode) => node.expandable;
  ngOnInit(): void {
  }

}
