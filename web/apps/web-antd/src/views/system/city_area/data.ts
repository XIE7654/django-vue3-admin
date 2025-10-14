import type { VxeTableGridOptions } from '@vben/plugins/vxe-table';

import type { VbenFormSchema } from '#/adapter/form';
import type { SystemCityAreaApi } from '#/models/system/city_area';

import { z } from '#/adapter/form';
import { $t } from '#/locales';

/**
 * 获取编辑表单的字段配置
 */
export function useSchema(): VbenFormSchema[] {
  return [
    {
      component: 'InputNumber',
      fieldName: 'prov_id',
      label: '省id',
    },
    {
      component: 'Input',
      fieldName: 'prov_name',
      label: '省',
      rules: z
        .string()
        .min(1, $t('ui.formRules.required', ['省']))
        .max(100, $t('ui.formRules.maxLength', ['省', 100])),
    },
    {
      component: 'InputNumber',
      fieldName: 'city_id',
      label: '市id',
    },
    {
      component: 'Input',
      fieldName: 'city_name',
      label: '市',
      rules: z
        .string()
        .min(1, $t('ui.formRules.required', ['市']))
        .max(100, $t('ui.formRules.maxLength', ['市', 100])),
    },
    {
      component: 'InputNumber',
      fieldName: 'area_id',
      label: '区id',
    },
    {
      component: 'Input',
      fieldName: 'area_name',
      label: '区',
      rules: z
        .string()
        .min(1, $t('ui.formRules.required', ['区']))
        .max(100, $t('ui.formRules.maxLength', ['区', 100])),
    },
    {
      component: 'Input',
      fieldName: 'remark',
      label: '备注',
      rules: z
        .string()
        .min(1, $t('ui.formRules.required', ['备注']))
        .max(100, $t('ui.formRules.maxLength', ['备注', 100])),
    },
  ];
}

/**
 * 获取编辑表单的字段配置
 */
export function useGridFormSchema(): VbenFormSchema[] {
  return [
    {
      component: 'InputNumber',
      fieldName: 'prov_id',
      label: '省id',
    },
    {
      component: 'Input',
      fieldName: 'prov_name',
      label: '省',
    },
    {
      component: 'InputNumber',
      fieldName: 'city_id',
      label: '市id',
    },
    {
      component: 'Input',
      fieldName: 'city_name',
      label: '市',
    },
    {
      component: 'InputNumber',
      fieldName: 'area_id',
      label: '区id',
    },
    {
      component: 'Input',
      fieldName: 'area_name',
      label: '区',
    },
  ];
}

/**
 * 获取表格列配置
 * @description 使用函数的形式返回列数据而不是直接export一个Array常量，是为了响应语言切换时重新翻译表头
 */
export function useColumns(): VxeTableGridOptions<SystemCityAreaApi.SystemCityArea>['columns'] {
  return [
    {
      field: 'id',
      title: 'ID',
    },
    {
      field: 'prov_id',
      title: '省id',
    },
    {
      field: 'prov_name',
      title: '省',
    },
    {
      field: 'city_id',
      title: '市id',
    },
    {
      field: 'city_name',
      title: '市',
    },
    {
      field: 'area_id',
      title: '区id',
    },
    {
      field: 'area_name',
      title: '区',
    },
  ];
}
