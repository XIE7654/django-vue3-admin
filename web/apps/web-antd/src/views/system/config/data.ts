import type { VxeTableGridOptions } from '@vben/plugins/vxe-table';

import type { VbenFormSchema } from '#/adapter/form';
import type { OnActionClickFn } from '#/adapter/vxe-table';
import type { SystemConfigApi } from '#/models/system/config';

import { z } from '#/adapter/form';
import { $t } from '#/locales';
import { format_datetime } from '#/utils/date';
import { op } from '#/utils/permission';

/**
 * 获取编辑表单的字段配置
 */
export function useSchema(): VbenFormSchema[] {
  return [
    {
      component: 'Input',
      fieldName: 'name',
      label: '参数名称',
      rules: z
        .string()
        .min(1, $t('ui.formRules.required', ['参数名称']))
        .max(100, $t('ui.formRules.maxLength', ['参数名称', 100])),
    },
    {
      component: 'Input',
      fieldName: 'key',
      label: '参数键名',
      rules: z
        .string()
        .min(1, $t('ui.formRules.required', ['参数键名']))
        .max(100, $t('ui.formRules.maxLength', ['参数键名', 100])),
    },
    {
      component: 'Input',
      fieldName: 'value',
      label: '参数键值',
      rules: z
        .string()
        .min(1, $t('ui.formRules.required', ['参数键值']))
        .max(100, $t('ui.formRules.maxLength', ['参数键值', 100])),
    },
    {
      component: 'RadioGroup',
      componentProps: {
        buttonStyle: 'solid',
        options: [
          { label: '开启', value: 1 },
          { label: '关闭', value: 0 },
        ],
        optionType: 'button',
      },
      defaultValue: 1,
      fieldName: 'config_type',
      label: '系统内置',
    },
    {
      component: 'Input',
      fieldName: 'remark',
      label: '备注'
    },
  ];
}

/**
 * 获取编辑表单的字段配置
 */
export function useGridFormSchema(): VbenFormSchema[] {
  return [
    {
      component: 'Input',
      fieldName: 'name',
      label: '参数名称',
    },
    {
      component: 'Input',
      fieldName: 'key',
      label: '参数键名',
    },
    {
      component: 'Input',
      fieldName: 'value',
      label: '参数键值',
    },
  ];
}

/**
 * 获取表格列配置
 * @description 使用函数的形式返回列数据而不是直接export一个Array常量，是为了响应语言切换时重新翻译表头
 * @param onActionClick 表格操作按钮点击事件
 */
export function useColumns(
  onActionClick?: OnActionClickFn<SystemConfigApi.SystemConfig>,
): VxeTableGridOptions<SystemConfigApi.SystemConfig>['columns'] {
  return [
    {
      field: 'id',
      title: 'ID',
    },
    {
      field: 'name',
      title: '参数名称',
    },
    {
      field: 'key',
      title: '参数键名',
    },
    {
      field: 'value',
      title: '参数键值',
    },
    {
      field: 'config_type',
      title: '系统内置',
    },
    {
      field: 'remark',
      title: '备注',
    },
    {
      field: 'create_time',
      title: '创建时间',
      width: 150,
      formatter: ({ cellValue }) => format_datetime(cellValue),
    },
    {
      align: 'center',
      cellRender: {
        attrs: {
          nameField: 'name',
          nameTitle: $t('system.config.name'),
          onClick: onActionClick,
        },
        name: 'CellOperation',
        options: [
          op('system:config:edit', 'edit'),
          op('system:config:delete', 'delete'),
        ],
      },
      field: 'action',
      fixed: 'right',
      title: '操作',
      width: 120,
    },
  ];
}
