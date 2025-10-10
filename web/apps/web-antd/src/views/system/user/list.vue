<script lang="ts" setup>
import {
  ACTION_ICON,
  type OnActionClickParams, TableAction,
  type VxeTableGridOptions,
} from '#/adapter/vxe-table';
import type { SystemUserApi } from '#/models/system/user';

import { Page, useVbenModal } from '@vben/common-ui';
import { Plus } from '@vben/icons';

import { Button, message } from 'ant-design-vue';

import { useVbenVxeGrid } from '#/adapter/vxe-table';
import { $t } from '#/locales';
import { SystemUserModel } from '#/models/system/user';

import { useColumns, useGridFormSchema } from './data';
import Form from './modules/form.vue';

const formModel = new SystemUserModel();

const [FormModal, formModalApi] = useVbenModal({
  connectedComponent: Form,
  destroyOnClose: true,
});

/**
 * 编辑用户数据
 */
function onEdit(row: SystemUserApi.SystemUser) {
  formModalApi.setData(row).open();
}

/**
 * 创建新用户数据
 */
function onCreate() {
  formModalApi.setData(null).open();
}

/**
 * 删除用户数据
 */
function onDelete(row: SystemUserApi.SystemUser) {
  const hideLoading = message.loading({
    content: '删除用户数据',
    duration: 0,
    key: 'action_process_msg',
  });
  formModel
    .delete(row.id)
    .then(() => {
      message.success({
        content: '删除成功',
        key: 'action_process_msg',
      });
      refreshGrid();
    })
    .catch(() => {
      hideLoading();
    });
}

/**
 * 表格操作按钮的回调函数
 */
function onActionClick({
  code,
  row,
}: OnActionClickParams<SystemUserApi.SystemUser>) {
  switch (code) {
    case 'delete': {
      onDelete(row);
      break;
    }
    case 'edit': {
      onEdit(row);
      break;
    }
  }
}

const [Grid, gridApi] = useVbenVxeGrid({
  formOptions: {
    wrapperClass: 'grid-cols-1 md:grid-cols-3 lg:grid-cols-4',
    schema: useGridFormSchema(),
    submitOnChange: true,
  },
  gridEvents: {},
  gridOptions: {
    columns: useColumns(onActionClick),
    height: 'auto',
    keepSource: true,
    pagerConfig: {
      enabled: true,
    },
    proxyConfig: {
      ajax: {
        query: async ({ page }, formValues) => {
          return await formModel.list({
            page: page.currentPage,
            pageSize: page.pageSize,
            ...formValues,
          });
        },
      },
    },
    toolbarConfig: {
      custom: true,
      export: false,
      refresh: { code: 'query' },
      zoom: true,
      search: true,
    },
  } as VxeTableGridOptions,
});

/**
 * 刷新表格
 */
function refreshGrid() {
  gridApi.query();
}
</script>

<template>
  <Page auto-content-height>
    <FormModal @success="refreshGrid" />
    <Grid table-title="用户数据">
      <template #toolbar-tools>
        <TableAction
          :actions="[
            {
              label: $t('ui.actionTitle.create', [$t('system.user.name')]),
              type: 'primary',
              icon: ACTION_ICON.ADD,
              auth: ['system:user:create'],
              onClick: onCreate,
            },
          ]"
        />
      </template>
    </Grid>
  </Page>
</template>
