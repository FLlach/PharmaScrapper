# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.1].define(version: 2026_08_31_042216) do
  # These are extensions that must be enabled in order to support this database
  enable_extension "pg_catalog.plpgsql"

  create_table "favorite_medicines", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.bigint "medicine_id", null: false
    t.datetime "updated_at", null: false
    t.bigint "user_id", null: false
    t.index ["medicine_id"], name: "index_favorite_medicines_on_medicine_id"
    t.index ["user_id"], name: "index_favorite_medicines_on_user_id"
  end

  create_table "medicines", force: :cascade do |t|
    t.string "active_ingredient"
    t.boolean "bioequivalent"
    t.datetime "created_at", null: false
    t.string "dosage"
    t.string "name"
    t.datetime "updated_at", null: false
  end

  create_table "pharmacies", force: :cascade do |t|
    t.boolean "active"
    t.string "base_domain"
    t.datetime "created_at", null: false
    t.string "logo_url"
    t.string "name"
    t.datetime "updated_at", null: false
  end

  create_table "pharmacy_products", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "image_url"
    t.bigint "medicine_id", null: false
    t.string "name"
    t.bigint "pharmacy_id", null: false
    t.string "sku"
    t.datetime "updated_at", null: false
    t.string "url"
    t.index ["medicine_id"], name: "index_pharmacy_products_on_medicine_id"
    t.index ["pharmacy_id"], name: "index_pharmacy_products_on_pharmacy_id"
  end

  create_table "price_histories", force: :cascade do |t|
    t.datetime "captured_at"
    t.datetime "created_at", null: false
    t.boolean "in_stock"
    t.bigint "pharmacy_product_id", null: false
    t.integer "price_offer"
    t.integer "price_regular"
    t.datetime "updated_at", null: false
    t.index ["pharmacy_product_id"], name: "index_price_histories_on_pharmacy_product_id"
  end

  create_table "sessions", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "ip_address"
    t.datetime "updated_at", null: false
    t.string "user_agent"
    t.bigint "user_id", null: false
    t.index ["user_id"], name: "index_sessions_on_user_id"
  end

  create_table "users", force: :cascade do |t|
    t.datetime "created_at", null: false
    t.string "email_address", null: false
    t.string "name"
    t.string "password_digest", null: false
    t.string "role", default: "standard"
    t.datetime "updated_at", null: false
    t.index ["email_address"], name: "index_users_on_email_address", unique: true
  end

  add_foreign_key "favorite_medicines", "medicines"
  add_foreign_key "favorite_medicines", "users"
  add_foreign_key "pharmacy_products", "medicines"
  add_foreign_key "pharmacy_products", "pharmacies"
  add_foreign_key "price_histories", "pharmacy_products"
  add_foreign_key "sessions", "users"
end
