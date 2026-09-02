module Api
  module V1
    class MedicinesController < ApplicationController
      allow_unauthenticated_access only: [:index, :comparison]

      def index
        scope = Medicine.all

        if params[:query].present?
          query = "%#{params[:query]}%"
          scope = scope.where("name ILIKE ? OR active_ingredient ILIKE ?", query, query)
        end

        limit_val = params[:limit].present? ? params[:limit].to_i : 50
        medicines = scope.limit(limit_val)

        med_ids = medicines.map(&:id)
        lowest_prices = PriceHistory.joins(:pharmacy_product)
          .where(pharmacy_products: { medicine_id: med_ids }, in_stock: true)
          .group("pharmacy_products.medicine_id")
          .select("pharmacy_products.medicine_id, MIN(COALESCE(price_histories.price_offer, price_histories.price_regular)) as min_price")
          .index_by(&:medicine_id)

        result = medicines.map do |med|
          min_p = lowest_prices[med.id]&.min_price
          med.as_json.merge(lowest_price: min_p)
        end

        render json: result, status: :ok
      end

      def comparison
        medicine = Medicine.find(params[:id])

        pharmacy_products = medicine.pharmacy_products.includes(:pharmacy)

        pharmacies = []
        price_history = []
        comparisons = []

        pharmacy_products.each do |product|
          latest_price = product.price_histories.order(captured_at: :desc).first
          next unless latest_price

          pharmacy_logo = product.pharmacy.respond_to?(:logo_url) ? product.pharmacy.logo_url : nil
          product_image = product.respond_to?(:image_url) ? product.image_url : nil
          product_link = product.respond_to?(:url) ? product.url : product.try(:product_url)

          pharmacies << {
            name: product.pharmacy.name,
            logo_url: pharmacy_logo,
            product_name: product.name,
            sku: product.sku,
            product_url: product_link,
            image_url: product_image,
            price_regular: latest_price.price_regular,
            price_offer: latest_price.price_offer,
            in_stock: latest_price.in_stock,
            last_captured_at: latest_price.captured_at
          }

          history_points = product.price_histories.order(captured_at: :asc).map do |ph|
            {
              date: ph.captured_at.strftime('%Y-%m-%d'),
              price: ph.price_offer || ph.price_regular,
              pharmacy: product.pharmacy.name
            }
          end
          price_history.concat(history_points)

          comparisons << {
            pharmacy_name: product.pharmacy.name,
            price: latest_price.price_offer || latest_price.price_regular,
            is_lowest: false,
            in_stock: latest_price.in_stock,
            url: product_link
          }
        end

        if comparisons.any?
          min_price = comparisons.map { |c| c[:price] }.compact.min
          comparisons.each do |c|
            c[:is_lowest] = (c[:price] == min_price)
          end
        end

        render json: {
          medicine: medicine,
          pharmacies: pharmacies,
          price_history: price_history,
          comparisons: comparisons
        }, status: :ok
      end
    end
  end
end
