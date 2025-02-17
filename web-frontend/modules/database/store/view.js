import _ from 'lodash'

import { StoreItemLookupError } from '@baserow/modules/core/errors'
import { uuid } from '@baserow/modules/core/utils/string'
import ViewService from '@baserow/modules/database/services/view'
import FilterService from '@baserow/modules/database/services/filter'
import SortService from '@baserow/modules/database/services/sort'
import { clone } from '@baserow/modules/core/utils/object'
import { DatabaseApplicationType } from '@baserow/modules/database/applicationTypes'

export function populateFilter(filter) {
  filter._ = {
    hover: false,
    loading: false,
  }
  return filter
}

export function populateSort(sort) {
  sort._ = {
    hover: false,
    loading: false,
  }
  return sort
}

export function populateView(view, registry) {
  const type = registry.get('view', view.type)

  view._ = {
    type: type.serialize(),
    selected: false,
    loading: false,
  }

  if (Object.prototype.hasOwnProperty.call(view, 'filters')) {
    view.filters.forEach((filter) => {
      populateFilter(filter)
    })
  } else {
    view.filters = []
  }

  if (Object.prototype.hasOwnProperty.call(view, 'sortings')) {
    view.sortings.forEach((sort) => {
      populateFilter(sort)
    })
  } else {
    view.sortings = []
  }

  return type.populate(view)
}

export const state = () => ({
  types: {},
  loading: false,
  loaded: false,
  items: [],
  selected: {},
})

export const mutations = {
  SET_ITEMS(state, applications) {
    state.items = applications
  },
  SET_LOADING(state, value) {
    state.loading = value
  },
  SET_ITEM_LOADING(state, { view, value }) {
    if (!Object.prototype.hasOwnProperty.call(view, '_')) {
      return
    }
    view._.loading = value
  },
  SET_LOADED(state, value) {
    state.loaded = value
  },
  ADD_ITEM(state, item) {
    state.items.push(item)
  },
  UPDATE_ITEM(state, { id, values }) {
    const index = state.items.findIndex((item) => item.id === id)
    Object.assign(state.items[index], state.items[index], values)
  },
  DELETE_ITEM(state, id) {
    const index = state.items.findIndex((item) => item.id === id)
    state.items.splice(index, 1)
  },
  SET_SELECTED(state, view) {
    Object.values(state.items).forEach((item) => {
      item._.selected = false
    })
    view._.selected = true
    state.selected = view
  },
  UNSELECT(state) {
    Object.values(state.items).forEach((item) => {
      item._.selected = false
    })
    state.selected = {}
  },
  ADD_FILTER(state, { view, filter }) {
    view.filters.push(filter)
  },
  FINALIZE_FILTER(state, { view, oldId, id }) {
    const index = view.filters.findIndex((item) => item.id === oldId)
    if (index !== -1) {
      view.filters[index].id = id
      view.filters[index]._.loading = false
    }
  },
  DELETE_FILTER(state, { view, id }) {
    const index = view.filters.findIndex((item) => item.id === id)
    if (index !== -1) {
      view.filters.splice(index, 1)
    }
  },
  DELETE_FIELD_FILTERS(state, { view, fieldId }) {
    for (let i = view.filters.length - 1; i >= 0; i--) {
      if (view.filters[i].field === fieldId) {
        view.filters.splice(i, 1)
      }
    }
  },
  UPDATE_FILTER(state, { filter, values }) {
    Object.assign(filter, filter, values)
  },
  SET_FILTER_LOADING(state, { filter, value }) {
    filter._.loading = value
  },
  ADD_SORT(state, { view, sort }) {
    view.sortings.push(sort)
  },
  FINALIZE_SORT(state, { view, oldId, id }) {
    const index = view.sortings.findIndex((item) => item.id === oldId)
    if (index !== -1) {
      view.sortings[index].id = id
      view.sortings[index]._.loading = false
    }
  },
  DELETE_SORT(state, { view, id }) {
    const index = view.sortings.findIndex((item) => item.id === id)
    if (index !== -1) {
      view.sortings.splice(index, 1)
    }
  },
  DELETE_FIELD_SORTINGS(state, { view, fieldId }) {
    for (let i = view.sortings.length - 1; i >= 0; i--) {
      if (view.sortings[i].field === fieldId) {
        view.sortings.splice(i, 1)
      }
    }
  },
  UPDATE_SORT(state, { sort, values }) {
    Object.assign(sort, sort, values)
  },
  SET_SORT_LOADING(state, { sort, value }) {
    sort._.loading = value
  },
}

export const actions = {
  /**
   * Changes the loading state of a specific view.
   */
  setItemLoading({ commit }, { view, value }) {
    commit('SET_ITEM_LOADING', { view, value })
  },
  /**
   * Fetches all the views of a given table. The is mostly called when the user
   * selects a different table.
   */
  async fetchAll({ commit, getters, dispatch, state }, table) {
    commit('SET_LOADING', true)
    commit('SET_LOADED', false)
    commit('UNSELECT', {})

    try {
      const { data } = await ViewService(this.$client).fetchAll(
        table.id,
        true,
        true
      )
      data.forEach((part, index, d) => {
        populateView(data[index], this.$registry)
      })
      commit('SET_ITEMS', data)
      commit('SET_LOADING', false)
      commit('SET_LOADED', true)
    } catch (error) {
      commit('SET_ITEMS', [])
      commit('SET_LOADING', false)

      throw error
    }
  },
  /**
   * Creates a new view with the provided type for the given table.
   */
  async create(
    { commit, getters, rootGetters, dispatch },
    { type, table, values }
  ) {
    if (Object.prototype.hasOwnProperty.call(values, 'type')) {
      throw new Error(
        'The key "type" is a reserved, but is already set on the ' +
          'values when creating a new view.'
      )
    }

    if (!this.$registry.exists('view', type)) {
      throw new Error(`A view with type "${type}" doesn't exist.`)
    }

    const postData = clone(values)
    postData.type = type

    const { data } = await ViewService(this.$client).create(table.id, postData)
    dispatch('forceCreate', { data })
  },
  /**
   * Forcefully create a new view without making a request to the server.
   */
  forceCreate({ commit }, { data }) {
    populateView(data, this.$registry)
    commit('ADD_ITEM', data)
  },
  /**
   * Updates the values of the view with the provided id.
   */
  async update({ commit, dispatch }, { view, values }) {
    const oldValues = {}
    const newValues = {}
    Object.keys(values).forEach((name) => {
      if (Object.prototype.hasOwnProperty.call(view, name)) {
        oldValues[name] = view[name]
        newValues[name] = values[name]
      }
    })

    dispatch('forceUpdate', { view, values: newValues })

    try {
      await ViewService(this.$client).update(view.id, values)
      commit('SET_ITEM_LOADING', { view, value: false })
    } catch (error) {
      dispatch('forceUpdate', { view, values: oldValues })
      throw error
    }
  },
  /**
   * Forcefully update an existing view without making a request to the backend.
   */
  forceUpdate({ commit }, { view, values }) {
    commit('UPDATE_ITEM', { id: view.id, values })
  },
  /**
   * Deletes an existing view with the provided id. A request to the server is first
   * made and after that it will be deleted from the store.
   */
  async delete({ commit, dispatch }, view) {
    try {
      await ViewService(this.$client).delete(view.id)
      dispatch('forceDelete', view)
    } catch (error) {
      // If the view to delete wasn't found we can just delete it from the
      // state.
      if (error.response && error.response.status === 404) {
        dispatch('forceDelete', view)
      } else {
        throw error
      }
    }
  },
  /**
   * Removes the view from the this store without making a delete request to the server.
   */
  forceDelete({ commit, dispatch, rootGetters }, view) {
    if (view._.selected) {
      commit('UNSELECT')

      const tableId = view.table.id
      const applications = rootGetters['application/getAll']
      let redirect = { name: 'dashboard' }

      // Try to find the table and database id so we can redirect back to the table
      // page. We might want to move this to a separate function.
      applications.forEach((application) => {
        if (application.type === DatabaseApplicationType.getType()) {
          application.tables.forEach((table) => {
            if (table.id === tableId) {
              redirect = {
                name: 'database-table',
                params: { databaseId: application.id, tableId: table.id },
              }
            }
          })
        }
      })

      // If the database id wasn't found we redirect to the dashboard.
      this.$router.push(redirect)
    }

    commit('DELETE_ITEM', view.id)
  },
  /**
   * Select a view and fetch all the applications related to that view. Note that
   * only the views of the selected table are stored in this store. It might be
   * possible you need to select the table first.
   */
  select({ commit, dispatch }, view) {
    commit('SET_SELECTED', view)
    return { view }
  },
  /**
   * Selects a view by a given view id. Note that only the views of the selected
   * table are stored in this store. It might be possible you need to select the
   * table first.
   */
  selectById({ dispatch, getters }, id) {
    const view = getters.get(id)
    if (view === undefined) {
      throw new StoreItemLookupError(`View with id ${id} is not found.`)
    }
    return dispatch('select', view)
  },
  /**
   * Changes the loading state of a specific filter.
   */
  setFilterLoading({ commit }, { filter, value }) {
    commit('SET_FILTER_LOADING', { filter, value })
  },
  /**
   * Creates a new filter and adds it to the store right away. If the API call succeeds
   * the row ID will be added, but if it fails it will be removed from the store.
   */
  async createFilter({ commit }, { view, field, values, emitEvent = true }) {
    // If the type is not provided we are going to choose the first available type.
    if (!Object.prototype.hasOwnProperty.call(values, 'type')) {
      const viewFilterTypes = this.$registry.getAll('viewFilter')
      const compatibleType = Object.values(viewFilterTypes).find(
        (viewFilterType) => {
          return viewFilterType.compatibleFieldTypes.includes(field.type)
        }
      )
      if (compatibleType === undefined) {
        throw new Error(
          `No compatible filter type could be found for field' ${field.type}`
        )
      }
      values.type = compatibleType.type
    }

    const filter = _.assign({}, values)
    populateFilter(filter)
    filter.id = uuid()
    filter._.loading = true

    commit('ADD_FILTER', { view, filter })

    try {
      const { data } = await FilterService(this.$client).create(view.id, values)
      commit('FINALIZE_FILTER', { view, oldId: filter.id, id: data.id })

      if (emitEvent) {
        this.$bus.$emit('view-filter-created', { view, filter })
      }
    } catch (error) {
      commit('DELETE_FILTER', { view, id: filter.id })
      throw error
    }

    return { filter }
  },
  /**
   * Forcefully create a new view filterwithout making a request to the backend.
   */
  forceCreateFilter({ commit }, { view, values }) {
    const filter = _.assign({}, values)
    populateFilter(filter)
    commit('ADD_FILTER', { view, filter })
  },
  /**
   * Updates the filter values in the store right away. If the API call fails the
   * changes will be undone.
   */
  async updateFilter({ dispatch, commit }, { filter, values }) {
    commit('SET_FILTER_LOADING', { filter, value: true })

    const oldValues = {}
    const newValues = {}
    Object.keys(values).forEach((name) => {
      if (Object.prototype.hasOwnProperty.call(filter, name)) {
        oldValues[name] = filter[name]
        newValues[name] = values[name]
      }
    })

    dispatch('forceUpdateFilter', { filter, values: newValues })

    try {
      await FilterService(this.$client).update(filter.id, values)
      commit('SET_FILTER_LOADING', { filter, value: false })
    } catch (error) {
      dispatch('forceUpdateFilter', { filter, values: oldValues })
      commit('SET_FILTER_LOADING', { filter, value: false })
      throw error
    }
  },
  /**
   * Forcefully update an existing view filter without making a request to the backend.
   */
  forceUpdateFilter({ commit }, { filter, values }) {
    commit('UPDATE_FILTER', { filter, values })
  },
  /**
   * Deletes an existing filter. A request to the server will be made first and
   * after that it will be deleted.
   */
  async deleteFilter({ dispatch, commit }, { view, filter }) {
    commit('SET_FILTER_LOADING', { filter, value: true })

    try {
      await FilterService(this.$client).delete(filter.id)
      dispatch('forceDeleteFilter', { view, filter })
    } catch (error) {
      commit('SET_FILTER_LOADING', { filter, value: false })
      throw error
    }
  },
  /**
   * Forcefully delete an existing field without making a request to the backend.
   */
  forceDeleteFilter({ commit }, { view, filter }) {
    commit('DELETE_FILTER', { view, id: filter.id })
  },
  /**
   * When a field is deleted the related filters are also automatically deleted in the
   * backend so they need to be removed here.
   */
  deleteFieldFilters({ commit, getters }, { field }) {
    getters.getAll.forEach((view) => {
      commit('DELETE_FIELD_FILTERS', { view, fieldId: field.id })
    })
  },
  /**
   * Changes the loading state of a specific sort.
   */
  setSortLoading({ commit }, { sort, value }) {
    commit('SET_SORT_LOADING', { sort, value })
  },
  /**
   * Creates a new sort and adds it to the store right away. If the API call succeeds
   * the row ID will be added, but if it fails it will be removed from the store.
   */
  async createSort({ commit }, { view, values }) {
    // If the order is not provided we are going to choose the ascending order.
    if (!Object.prototype.hasOwnProperty.call(values, 'order')) {
      values.order = 'ASC'
    }

    const sort = _.assign({}, values)
    populateSort(sort)
    sort.id = uuid()
    sort._.loading = true

    commit('ADD_SORT', { view, sort })

    try {
      const { data } = await SortService(this.$client).create(view.id, values)
      commit('FINALIZE_SORT', { view, oldId: sort.id, id: data.id })
    } catch (error) {
      commit('DELETE_SORT', { view, id: sort.id })
      throw error
    }

    return { sort }
  },
  /**
   * Forcefully create a new  view sorting without making a request to the backend.
   */
  forceCreateSort({ commit }, { view, values }) {
    const sort = _.assign({}, values)
    populateSort(sort)
    commit('ADD_SORT', { view, sort })
  },
  /**
   * Updates the sort values in the store right away. If the API call fails the
   * changes will be undone.
   */
  async updateSort({ dispatch, commit }, { sort, values }) {
    commit('SET_SORT_LOADING', { sort, value: true })

    const oldValues = {}
    const newValues = {}
    Object.keys(values).forEach((name) => {
      if (Object.prototype.hasOwnProperty.call(sort, name)) {
        oldValues[name] = sort[name]
        newValues[name] = values[name]
      }
    })

    dispatch('forceUpdateSort', { sort, values: newValues })

    try {
      await SortService(this.$client).update(sort.id, values)
      commit('SET_SORT_LOADING', { sort, value: false })
    } catch (error) {
      dispatch('forceUpdateSort', { sort, values: oldValues })
      commit('SET_SORT_LOADING', { sort, value: false })
      throw error
    }
  },
  /**
   * Forcefully update an existing view sort without making a request to the backend.
   */
  forceUpdateSort({ commit }, { sort, values }) {
    commit('UPDATE_SORT', { sort, values })
  },
  /**
   * Deletes an existing sort. A request to the server will be made first and
   * after that it will be deleted.
   */
  async deleteSort({ dispatch, commit }, { view, sort }) {
    commit('SET_SORT_LOADING', { sort, value: true })

    try {
      await SortService(this.$client).delete(sort.id)
      dispatch('forceDeleteSort', { view, sort })
    } catch (error) {
      commit('SET_SORT_LOADING', { sort, value: false })
      throw error
    }
  },
  /**
   * Forcefully delete an existing view sort without making a request to the backend.
   */
  forceDeleteSort({ commit }, { view, sort }) {
    commit('DELETE_SORT', { view, id: sort.id })
  },
  /**
   * When a field is deleted the related sortings are also automatically deleted in the
   * backend so they need to be removed here.
   */
  deleteFieldSortings({ commit, getters }, { field }) {
    getters.getAll.forEach((view) => {
      commit('DELETE_FIELD_SORTINGS', { view, fieldId: field.id })
    })
  },
  /**
   * Is called when a field is updated. It will check if there are filters related
   * to the delete field.
   */
  fieldUpdated({ dispatch, commit, getters }, { field, fieldType }) {
    // Remove all filters are not compatible anymore.
    getters.getAll.forEach((view) => {
      view.filters
        .filter((filter) => filter.field === field.id)
        .forEach((filter) => {
          const filterType = this.$registry.get('viewFilter', filter.type)
          const compatible = filterType.compatibleFieldTypes.includes(
            fieldType.type
          )
          if (!compatible) {
            commit('DELETE_FILTER', { view, id: filter.id })
          }
        })
    })

    // Remove all the field sortings because the new field does not support sortings
    // at all.
    if (!fieldType.canSortInView) {
      dispatch('deleteFieldSortings', { field })
    }
  },
  /**
   * Is called when a field is deleted. It will remove all filters and sortings
   * related to the field.
   */
  fieldDeleted({ dispatch }, { field }) {
    dispatch('deleteFieldFilters', { field })
    dispatch('deleteFieldSortings', { field })
  },
}

export const getters = {
  hasSelected(state) {
    return Object.prototype.hasOwnProperty.call(state.selected, '_')
  },
  getSelected(state) {
    return state.selected
  },
  getSelectedId(state) {
    return state.selected.id || 0
  },
  isLoaded(state) {
    return state.loaded
  },
  get: (state) => (id) => {
    return state.items.find((item) => item.id === id)
  },
  first(state) {
    return state.items.length > 0 ? state.items[0] : null
  },
  getAll(state) {
    return state.items
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}
