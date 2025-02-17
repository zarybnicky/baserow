<template>
  <div
    class="grid-view__column"
    :class="{
      'grid-view__column--filtered':
        !view.filters_disabled &&
        view.filters.findIndex((filter) => filter.field === field.id) !== -1,
      'grid-view__column--sorted':
        view.sortings.findIndex((sort) => sort.field === field.id) !== -1,
    }"
  >
    <div
      class="grid-view__description"
      :class="{ 'grid-view__description--loading': field._.loading }"
    >
      <div class="grid-view__description-icon">
        <i class="fas" :class="'fa-' + field._.type.iconClass"></i>
      </div>
      <div class="grid-view__description-name">{{ field.name }}</div>
      <a
        ref="contextLink"
        class="grid-view__description-options"
        @click="$refs.context.toggle($refs.contextLink, 'bottom', 'right', 0)"
      >
        <i class="fas fa-caret-down"></i>
      </a>
      <FieldContext
        ref="context"
        :table="table"
        :field="field"
        @update="$emit('refresh', $event)"
        @delete="$emit('refresh')"
      >
        <li v-if="canFilter">
          <a @click="createFilter($event, view, field)">
            <i class="context__menu-icon fas fa-fw fa-filter"></i>
            Create filter
          </a>
        </li>
        <li v-if="field._.type.canSortInView">
          <a @click="createSort($event, view, field, 'ASC')">
            <i class="context__menu-icon fas fa-fw fa-sort-amount-down-alt"></i>
            Sort
            <template v-if="field._.type.sortIndicator[0] === 'text'">{{
              field._.type.sortIndicator[1]
            }}</template>
            <i
              v-if="field._.type.sortIndicator[0] === 'icon'"
              class="fa"
              :class="'fa-' + field._.type.sortIndicator[1]"
            ></i>
            <i class="fas fa-long-arrow-alt-right"></i>
            <template v-if="field._.type.sortIndicator[0] === 'text'">{{
              field._.type.sortIndicator[2]
            }}</template>
            <i
              v-if="field._.type.sortIndicator[0] === 'icon'"
              class="fa"
              :class="'fa-' + field._.type.sortIndicator[2]"
            ></i>
          </a>
        </li>
        <li v-if="field._.type.canSortInView">
          <a @click="createSort($event, view, field, 'DESC')">
            <i class="context__menu-icon fas fa-fw fa-sort-amount-down"></i>
            Sort
            <template v-if="field._.type.sortIndicator[0] === 'text'">{{
              field._.type.sortIndicator[2]
            }}</template>
            <i
              v-if="field._.type.sortIndicator[0] === 'icon'"
              class="fa"
              :class="'fa-' + field._.type.sortIndicator[2]"
            ></i>
            <i class="fas fa-long-arrow-alt-right"></i>
            <template v-if="field._.type.sortIndicator[0] === 'text'">{{
              field._.type.sortIndicator[1]
            }}</template>
            <i
              v-if="field._.type.sortIndicator[0] === 'icon'"
              class="fa"
              :class="'fa-' + field._.type.sortIndicator[1]"
            ></i>
          </a>
        </li>
        <li v-if="!field.primary && canFilter">
          <a @click="hide($event, view, field)">
            <i class="context__menu-icon fas fa-fw fa-eye-slash"></i>
            Hide field
          </a>
        </li>
      </FieldContext>
      <slot></slot>
    </div>
  </div>
</template>

<script>
import { notifyIf } from '@baserow/modules/core/utils/error'
import FieldContext from '@baserow/modules/database/components/field/FieldContext'

export default {
  name: 'GridViewFieldType',
  components: { FieldContext },
  props: {
    table: {
      type: Object,
      required: true,
    },
    view: {
      type: Object,
      required: true,
    },
    field: {
      type: Object,
      required: true,
    },
  },
  computed: {
    canFilter() {
      const filters = Object.values(this.$registry.getAll('viewFilter'))
      for (const type in filters) {
        if (filters[type].compatibleFieldTypes.includes(this.field.type)) {
          return true
        }
      }
      return false
    },
  },
  methods: {
    async createFilter(event, view, field) {
      // Prevent the event from propagating to the body so that it does not close the
      // view filter context menu right after it has been opened. This is due to the
      // click outside event that is fired there.
      event.stopPropagation()
      event.preventDefault()
      this.$refs.context.hide()

      try {
        await this.$store.dispatch('view/createFilter', {
          view,
          field,
          values: {
            field: field.id,
            value: '',
          },
        })
        this.$emit('refresh')
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    async createSort(event, view, field, order) {
      // Prevent the event from propagating to the body so that it does not close the
      // view filter context menu right after it has been opened. This is due to the
      // click outside event that is fired there.
      event.stopPropagation()
      event.preventDefault()
      this.$refs.context.hide()

      const sort = view.sortings.find((sort) => sort.field === this.field.id)
      const values = {
        field: field.id,
        order,
      }

      try {
        if (sort === undefined) {
          await this.$store.dispatch('view/createSort', { view, field, values })
        } else {
          await this.$store.dispatch('view/updateSort', { sort, values })
        }

        this.$emit('refresh')
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
    async hide(event, view, field) {
      try {
        await this.$store.dispatch('view/grid/updateFieldOptionsOfField', {
          gridId: view.id,
          field,
          values: { hidden: true },
          oldValues: { hidden: false },
        })
      } catch (error) {
        notifyIf(error, 'view')
      }
    },
  },
}
</script>
