module Api
  module V1
    class MedicinesController < ApplicationController
      allow_unauthenticated_access only: [:index, :comparison]

      def index
        medicines = Medicine.all
        if params[:query].present?
          medicines = medicines.where("name ILIKE ? OR active_ingredient ILIKE ?", "%#{params[:query]}%", "%#{params[:query]}%")
        end

        # In a real app we'd order by cheapest pharmacy product, but for now we'll just return medicines
        render json: medicines, status: :ok
      end

      def comparison
        medicine = Medicine.find(params[:id])

        pharmacy_products = medicine.pharmacy_products.includes(:pharmacy, :price_histories)

        comparison_data = pharmacy_products.map do |product|
          # Using max_by on the loaded association avoids N+1 queries
          latest_price = product.price_histories.max_by(&:captured_at)

          {
            pharmacy: product.pharmacy.name,
            pharmacy_logo: product.pharmacy.logo_url,
            product_name: product.name,
            sku: product.sku,
            url: product.url,
            image_url: product.image_url,
            current_price_regular: latest_price&.price_regular,
            current_price_offer: latest_price&.price_offer,
            in_stock: latest_price&.in_stock,
            last_captured_at: latest_price&.captured_at
          }
        end

        render json: {
          medicine: medicine,
          comparisons: comparison_data.sort_by { |c| c[:current_price_offer] || c[:current_price_regular] || Float::INFINITY }
        }, status: :ok
      rescue ActiveRecord::RecordNotFound
        render json: { error: "Medicine not found" }, status: :not_found
      end
    end
  end
end
