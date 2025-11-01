import { computed, ref } from 'vue';

import { $t } from '@vben/locales';

import { useVbenModal } from '@vben-core/popup-ui';

import { useVbenForm } from '#/adapter/form';
import { BaseModel } from '#/models';

export interface BaseEntity {
  id?: number;
  // 其他公共字段...
}

export function useModelForm<T extends BaseEntity>(options: {
  model: BaseModel<T>;
  schema: any;
  titleKey: string;
}) {
  const formData = ref<T>();
  const emit = defineEmits(['success']);

  const getTitle = computed(() => {
    return formData.value?.id
      ? $t('ui.actionTitle.edit', [$t(options.titleKey)])
      : $t('ui.actionTitle.create', [$t(options.titleKey)]);
  });

  const [Form, formApi] = useVbenForm({
    layout: 'horizontal',
    schema: options.schema,
    showDefaultActions: false,
  });

  const [Modal, modalApi] = useVbenModal({
    async onConfirm() {
      const { valid } = await formApi.validate();
      if (valid) {
        modalApi.lock();
        const rawFormData = await formApi.getValues();
        const formattedData = rawFormData as Partial<T>; // 关键：类型断言

        try {
          await (formData.value?.id
            ? options.model.update(formData.value.id, formattedData)
            : options.model.create(formattedData as Omit<T, any>));
          await modalApi.close();
          emit('success');
        } finally {
          modalApi.lock(false);
        }
      }
    },
    onOpenChange(isOpen) {
      if (isOpen) {
        const data = modalApi.getData<T>();
        if (data) {
          formData.value = data;
          formApi.setValues(formData.value);
        }
      }
    },
  });

  function resetForm() {
    formApi.resetForm();
    formApi.setValues(formData.value || {});
  }

  return {
    Form,
    Modal,
    formData,
    getTitle,
    resetForm,
    formApi,
    modalApi,
  };
}
